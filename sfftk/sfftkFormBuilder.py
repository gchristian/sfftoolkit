# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class sfftkMainFrame
###########################################################################

class sfftkMainFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

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

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def showAbout( self, event ):
		event.Skip()

	def onQuit( self, event ):
		event.Skip()


###########################################################################
## Class sfftkPanel
###########################################################################

class sfftkPanel ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 549,499 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		mainSizer = wx.BoxSizer( wx.VERTICAL )

		self.deckPage = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		decksMainSizer = wx.BoxSizer( wx.VERTICAL )

		deckListCtrlChoices = []
		self.deckListCtrl = wx.CheckListBox( self.deckPage, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), deckListCtrlChoices, 0 )
		self.deckListCtrl.SetMinSize( wx.Size( 600,-1 ) )

		decksMainSizer.Add( self.deckListCtrl, 1, wx.ALL, 5 )

		decksFirstHSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.userLbl = wx.StaticText( self.deckPage, wx.ID_ANY, u"SF User Name: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.userLbl.Wrap( -1 )

		decksFirstHSizer.Add( self.userLbl, 0, wx.ALL, 5 )

		self.userCtrl = wx.TextCtrl( self.deckPage, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 240,-1 ), 0 )
		decksFirstHSizer.Add( self.userCtrl, 0, wx.ALL, 5 )

		self.ignoreCache = wx.CheckBox( self.deckPage, wx.ID_ANY, u"Overwite Cache", wx.DefaultPosition, wx.DefaultSize, 0 )
		decksFirstHSizer.Add( self.ignoreCache, 0, wx.ALL, 5 )


		decksMainSizer.Add( decksFirstHSizer, 0, wx.EXPAND, 5 )

		mainSecondHSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.addUserBtn = wx.Button( self.deckPage, wx.ID_ANY, u"Add Decks for User", wx.DefaultPosition, wx.DefaultSize, 0 )
		mainSecondHSizer.Add( self.addUserBtn, 0, wx.ALL, 5 )

		self.addDeckBtn = wx.Button( self.deckPage, wx.ID_ANY, u"Add Deck by ID", wx.DefaultPosition, wx.DefaultSize, 0 )
		mainSecondHSizer.Add( self.addDeckBtn, 0, wx.ALL, 5 )


		decksMainSizer.Add( mainSecondHSizer, 0, wx.EXPAND, 5 )

		self.sfftkTab = wx.Notebook( self.deckPage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SFFDividerPage = wx.Panel( self.sfftkTab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		diviederMainSizer = wx.BoxSizer( wx.VERTICAL )

		dividerFirstHSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.HeightLbl = wx.StaticText( self.SFFDividerPage, wx.ID_ANY, u"Height", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.HeightLbl.Wrap( -1 )

		dividerFirstHSizer.Add( self.HeightLbl, 0, wx.ALL, 5 )

		self.heightCtrl = wx.SpinCtrlDouble( self.SFFDividerPage, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2.5, 3.3, 2.900000, 0.05 )
		self.heightCtrl.SetDigits( 2 )
		dividerFirstHSizer.Add( self.heightCtrl, 0, wx.ALL, 5 )


		diviederMainSizer.Add( dividerFirstHSizer, 0, wx.EXPAND, 5 )

		self.factionSeperatorCheckbox = wx.CheckBox( self.SFFDividerPage, wx.ID_ANY, u"Include Faction Seperators", wx.DefaultPosition, wx.DefaultSize, 0 )
		diviederMainSizer.Add( self.factionSeperatorCheckbox, 0, wx.ALL, 5 )

		layoutChoiceCtrlChoices = [ u"Tab: Name, Rarity, Spells; Body: Creatures", u"Tab: Name, Rarity, Spell, Creatures", u"Tab: Name, Spell, Creatures" ]
		self.layoutChoiceCtrl = wx.Choice( self.SFFDividerPage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, layoutChoiceCtrlChoices, 0 )
		self.layoutChoiceCtrl.SetSelection( 0 )
		diviederMainSizer.Add( self.layoutChoiceCtrl, 0, wx.ALL, 5 )

		divSortCtrlChoices = [ u"Sort by Faction then Deck", u"Sort by Deck" ]
		self.divSortCtrl = wx.Choice( self.SFFDividerPage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, divSortCtrlChoices, 0 )
		self.divSortCtrl.SetSelection( 0 )
		diviederMainSizer.Add( self.divSortCtrl, 0, wx.ALL, 5 )

		buttonHSizer = wx.BoxSizer( wx.HORIZONTAL )


		buttonHSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.createDivBtn = wx.Button( self.SFFDividerPage, wx.ID_ANY, u"Create", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.createDivBtn.SetBitmapPosition( wx.RIGHT )
		buttonHSizer.Add( self.createDivBtn, 0, wx.ALL, 5 )


		diviederMainSizer.Add( buttonHSizer, 1, wx.EXPAND, 5 )


		self.SFFDividerPage.SetSizer( diviederMainSizer )
		self.SFFDividerPage.Layout()
		diviederMainSizer.Fit( self.SFFDividerPage )
		self.sfftkTab.AddPage( self.SFFDividerPage, u"Dividers", True )
		self.SFFDeckNavigator = wx.Panel( self.sfftkTab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		navigatorMainSizer = wx.BoxSizer( wx.VERTICAL )

		self.overviewCtrl = wx.CheckBox( self.SFFDeckNavigator, wx.ID_ANY, u"Include Printable Deck Summaries", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.overviewCtrl.SetValue(True)
		navigatorMainSizer.Add( self.overviewCtrl, 0, wx.ALL, 5 )

		self.imagesCtrl = wx.CheckBox( self.SFFDeckNavigator, wx.ID_ANY, u"Include Card Images", wx.DefaultPosition, wx.DefaultSize, 0 )
		navigatorMainSizer.Add( self.imagesCtrl, 0, wx.ALL, 5 )

		buttonHSizer2 = wx.BoxSizer( wx.HORIZONTAL )


		buttonHSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.deckNavBtn = wx.Button( self.SFFDeckNavigator, wx.ID_ANY, u"Create", wx.DefaultPosition, wx.DefaultSize, 0 )
		buttonHSizer2.Add( self.deckNavBtn, 0, wx.ALL, 5 )


		navigatorMainSizer.Add( buttonHSizer2, 1, wx.EXPAND, 5 )


		self.SFFDeckNavigator.SetSizer( navigatorMainSizer )
		self.SFFDeckNavigator.Layout()
		navigatorMainSizer.Fit( self.SFFDeckNavigator )
		self.sfftkTab.AddPage( self.SFFDeckNavigator, u"Browser / Summary", False )

		decksMainSizer.Add( self.sfftkTab, 0, wx.EXPAND |wx.ALL, 5 )


		self.deckPage.SetSizer( decksMainSizer )
		self.deckPage.Layout()
		decksMainSizer.Fit( self.deckPage )
		mainSizer.Add( self.deckPage, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( mainSizer )
		self.Layout()

		# Connect Events
		self.addUserBtn.Bind( wx.EVT_BUTTON, self.addDecksForUser )
		self.addDeckBtn.Bind( wx.EVT_BUTTON, self.addDeckByID )
		self.createDivBtn.Bind( wx.EVT_BUTTON, self.createDividers )
		self.deckNavBtn.Bind( wx.EVT_BUTTON, self.createDeckNavigator )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def addDecksForUser( self, event ):
		event.Skip()

	def addDeckByID( self, event ):
		event.Skip()

	def createDividers( self, event ):
		event.Skip()

	def createDeckNavigator( self, event ):
		event.Skip()


