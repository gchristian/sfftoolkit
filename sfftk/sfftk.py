from unittest import skip
import wx
from wx.adv import AboutBox, AboutDialogInfo
from sfftkFormBuilder import sfftkPanel
from sffCollection import sffCollection
import requests
import json
import pathlib

class SFFTK(sfftkPanel):

	def __init__(self, parent):
		super().__init__(parent)
		self.collection = sffCollection()

		self.icon = wx.Icon(self.collection.icon,wx.BITMAP_TYPE_ICO)
		#self.icon.LoadFile(self.collection.icon,wx.BITMAP_TYPE_ICON)

		self.deckListCtrl.Clear()
		if len(self.collection.getDeckNames()) > 1:
			self.deckListCtrl.InsertItems(self.collection.getDeckNames(),0)

		self.readDefaults()

		#self.Bind(wx.EVT_CLOSE, self.OnClose)

	def readDefaults(self):
		config = wx.Config("SFToolKit")
		self.userCtrl.SetValue(config.Read("SFFUser"))

	def saveDefaults(self):
		config = wx.Config("SFToolKit")
		config.Write("SFFUser", self.userCtrl.Value)
	
	#def OnClose(self, event):
	#	print("closing time")
	#	self.saveDefaults()
	#	event.skip()
		

	def addDeckByID( self, event ):

		
		user = self.userCtrl.Value
		user_provided_id = None

		if user == "":
			failed = wx.MessageDialog(self, "You must populate your User name first.", caption="No User")
			failed.ShowModal()
			return
			

		dlg = wx.TextEntryDialog(None, 'Enter Deck ID',
				'Add Deck by ID', '')
		while user_provided_id is None:
			dlg_action = dlg.ShowModal()
			if dlg_action == wx.ID_OK:
				user_provided_id = str(dlg.GetValue())
			else:
				return

		if self.ignoreCache.IsChecked() == False:
			if self.collection.containsDeck(user_provided_id) == True:
				skipped = wx.MessageDialog(self, "Deck exists, force download again by enabling Overwrite Cache option.", caption="Skipped Deck")
				skipped.ShowModal()
				return

		headers={'Accept' : 'application/json','Content-Type': 'application/json'}

		try:
			r = requests.get("https://ul51g2rg42.execute-api.us-east-1.amazonaws.com/main/deck/"+user_provided_id+"?inclCards=true&inclUsers=true&username="+user,
						headers=headers)	
			try:
				response_content = json.loads(r.content)
				if "id" in response_content:
					if response_content["id"] == user_provided_id:
						if self.collection.addDeckFromJSON(response_content):
							self.deckListCtrl.InsertItems([response_content["name"]],0)
							created = wx.MessageDialog(self, response_content["name"] + " has been downloaded with " + user_provided_id, caption="Deck Downloaded")
							created.ShowModal()
							return
				failed = wx.MessageDialog(self, "Response from server is not what we expected. " + r.content.decode("utf-8") , caption="Failed to add Deck")
				failed.ShowModal()
				return
			except Exception as e:
				print(e)
				failed = wx.MessageDialog(self, "Response from server not what we expected. " + r.content.decode("utf-8") , caption="Failed to add Deck")
				failed.ShowModal()
				return
		except Exception as e:
			print(e)
		
		failed = wx.MessageDialog(self, "Unknown error. Check network is active and SolForge site is up. More info in logs.", caption="Failed to add Deck")
		failed.ShowModal()

	def addDecksForUser( self, event ):
		user = self.userCtrl.Value
	

		if user == "":
			failed = wx.MessageDialog(self, "You must populate your User name first.", caption="No User")
			failed.ShowModal()
			return
			
		headers={'Accept' : 'application/json','Content-Type': 'application/json'}

		r = requests.get("https://ul51g2rg42.execute-api.us-east-1.amazonaws.com/main/deck/?pageSize=100&inclCards=true&username="+user,
						headers=headers)
		try:
			response_content = json.loads(r.content)
			decksAdded = 0
			decksSkipped = 0
			decksFailed = 0

			if "Items" in response_content:
				for item in response_content["Items"]:
					if self.ignoreCache.IsChecked() == False:
						if self.collection.containsDeck(item.get("id","")) == True:
							decksSkipped = decksSkipped + 1
							continue
					if self.collection.addDeckFromJSON(item):
						decksAdded = decksAdded + 1
						self.deckListCtrl.InsertItems([item["name"]],0)
					else:
						decksFailed = decksFailed + 1

				completed = wx.MessageDialog(self, "%i decks added\n %i decks skipped\n%i decks failed" % (decksAdded, decksSkipped, decksFailed), caption="Finished Processing User")
				completed.ShowModal()
			else:
				failed = wx.MessageDialog(self, "Response from server not what we expected." + r.content.decode("utf-8") , caption="Failed Prcoessing User")
				failed.ShowModal()
		except Exception as e:
			print(e)

	def createDividers( self, event ):

		with wx.FileDialog(self, "Save divider PDF file as",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,wildcard="PDF files (*.pdf)|*.pdf") as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			saveAsPath = fileDialog.GetPath()
			
			if "pdf" not in pathlib.Path(saveAsPath).suffix:
				saveAsPath = saveAsPath + ".pdf"

			self.collection.renderDividerPDF(saveAsPath,
											self.heightCtrl.Value,
											self.factionSeperatorCheckbox.Value,
											sort=self.divSortCtrl.GetSelection(),
											layout=self.layoutChoiceCtrl.GetSelection()
											)


	def createDeckNavigator( self, event ):
		with wx.DirDialog(self, "Select folder to create site in:",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dirDialog:

			if dirDialog.ShowModal() == wx.ID_CANCEL:
				return

			self.collection.generateDeckNavigator(dirDialog.GetPath())

	def extractCards( self, event ):
		with wx.DirDialog(self, "Select folder to create images in:",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dirDialog:

			if dirDialog.ShowModal() == wx.ID_CANCEL:
				return

			pDialog = wx.ProgressDialog("Extracting cards", "Downloading non-cached images", 100,
					style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
			pDialog.SetMinSize((600,-1))
			pDialog.ShowModal()

			self.downloadMissingAssets()

			print(self.cardNameCtrl.GetSelection())

			self.collection.parseCardsFromDeckImages(dirDialog.GetPath(),pDialog=pDialog,nameSchema=self.cardNameCtrl.GetSelection())

			pDialog.Destroy()



	def downloadMissingAssets(self):

		downloadTuples = self.collection.missingImages()
		print(downloadTuples)

		for dt in downloadTuples:
			try:
				response = requests.get(dt[0])
				with open(dt[1], "wb") as file:
					file.write(response.content)
			except:
				print("error downloading " + dt[0] + " to " + dt[1])


class MainFrame(wx.Frame):

	def __init__(self):
		super().__init__(None, title="Solforge Fusion Toolkit", size=(600,600))

		self.panel = SFFTK(self)
		self.Show()
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		self.sfftkMenuBar = wx.MenuBar( 0 )
		self.sfftkMenu = wx.Menu()
		self.aboutItem = wx.MenuItem( self.sfftkMenu, wx.ID_ABOUT, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.sfftkMenu.Append( self.aboutItem )

		self.sfftkMenu.AppendSeparator()

		self.quiteItem = wx.MenuItem( self.sfftkMenu, wx.ID_EXIT, u"Quit"+ u"\t" + u"CTRL-Q", wx.EmptyString, wx.ITEM_NORMAL )
		self.sfftkMenu.Append( self.quiteItem )

		self.sfftkMenuBar.Append( self.sfftkMenu, u"File" )

		self.SetMenuBar( self.sfftkMenuBar )


		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.showAbout, id = self.aboutItem.GetId() )
		self.Bind( wx.EVT_MENU, self.onQuit, id = self.quiteItem.GetId() )
	
	def OnClose(self, event):
		self.panel.saveDefaults()
		event.Skip()
	
	def onQuit(self, event):
		self.close()
		event.Skip()

	def showAbout(self, event):
		aboutInfo = AboutDialogInfo()
		aboutInfo.SetName("SFF Tool Kit")
		aboutInfo.SetVersion("0.1")
		aboutInfo.SetDescription("")
		aboutInfo.SetCopyright("(C) 2022 Gorman Christian")
		aboutInfo.SetWebSite("")
		aboutInfo.AddDeveloper("Gorman Christian with thanks to (and no affiliation):")
		aboutInfo.AddDeveloper("reportlab https://www.reportlab.com/opensource/")
		aboutInfo.AddDeveloper("requests https://requests.readthedocs.io/en/latest/")
		aboutInfo.AddDeveloper("wxWidgets https://wxwidgets.org/about/licence/")
		aboutInfo.AddDeveloper("wxPython https://wxpython.org/")	
		aboutInfo.AddDeveloper("appdirs  https://github.com/ActiveState/appdirs")
		aboutInfo.AddDeveloper("Stoneblade https://www.stoneblade.com")
		aboutInfo.AddArtist("Icon base ToolBox from Vector.me https://Vector.me")
		aboutInfo.AddArtist("Symbols/Artwork/SFF Logo https://www.stoneblade.com")
		aboutInfo.SetIcon(self.panel.icon)

		AboutBox(aboutInfo)

	def onQuit(self, event):
		self.Close()


if __name__ == '__main__':
	app = wx.App(redirect=False)
	frame = MainFrame()
	app.MainLoop()