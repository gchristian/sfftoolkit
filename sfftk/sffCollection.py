import json
import os
from appdirs import user_data_dir
from pathlib import Path
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from PIL import Image
import shutil
import sys

from operator import itemgetter

class sffCollection(object):
	def __init__(self):
		super().__init__()
		
		#use the handy appdirs library to find platform appdata location and set local paths
		self.appData = user_data_dir(appname="SFFToolKit")
		self.cacheFolder = os.path.join(self.appData,"Cache")

		if sys.platform == 'darwin':
			self.resourcePath =  os.path.join(os.environ['RESOURCEPATH'],"data")
		else:
			self.resourcePath =  os.path.join(os.path.dirname(__file__),"data")

		self.icon = os.path.join(self.resourcePath,"icon.ico")


		#make sure needed folders exist
		Path(self.appData).mkdir(parents=True, exist_ok=True)
		Path(self.cacheFolder).mkdir(parents=True, exist_ok=True)

		self.faction_icons = {

			"Nekrium" : os.path.join(self.resourcePath,"nekrium.png"),
			"Alloyin" : os.path.join(self.resourcePath,"alloyin.png"),
			"Tempys" : os.path.join(self.resourcePath,"tempys.png"),
			"Uterra" : os.path.join(self.resourcePath,"uterra.png")
		}

		self.rarity_icons = {

			"Common" : os.path.join(self.resourcePath,"S1_Common.png"),
			"Common Common" : os.path.join(self.resourcePath,"S1_CommonCommon.png"),
			"Common Rare" : os.path.join(self.resourcePath,"S1_CommonRare.png"),
			"Rare" : os.path.join(self.resourcePath,"S1_Rare.png"),
			"Rare Rare" : os.path.join(self.resourcePath,"S1_RareRare.png"),
			"Rare Common" : os.path.join(self.resourcePath,"S1_RareCommon.png"),
			"LS" : os.path.join(self.resourcePath,"S1_LS.png")
		}

		#load decks from cache
		self.deckNames = []
		self.decks = self.loadCachedDecks()
		self.refreshStats()


	def getDeckNames(self):
		return self.deckNames

	def loadCachedDecks(self):
		decks = []

		for item in os.scandir(self.cacheFolder):
			if item.is_file() and item.name[len(item.name)-4:] == 'json':
				with open(item.path, 'r') as deck_file:
					deck = json.load(deck_file)
					decks.append(deck)
					self.deckNames.append(deck["name"])
		return decks

	def containsDeck(self, id):
		return os.path.isfile(os.path.join(self.cacheFolder,id+".json"))


	def addDeckFromJSON(self, jsonData):
		if "id" not in jsonData:
			return False
		with open(os.path.join(self.cacheFolder,jsonData["id"]+".json"), 'w', encoding='utf-8') as deck_file:
			json.dump(jsonData, deck_file, ensure_ascii=False, indent=4)
			self.decks.append(jsonData)
			self.deckNames.append(jsonData["name"])

			self.refreshStats()

			return True
		
	def removeDeckByName(self, nameofdeck):
		for deck in self.decks:
			if deck["name"] == nameofdeck:
				for file in Path(self.cacheFolder).glob(deck["id"] + "*"):
					file.unlink()
				self.decks.remove(deck)
	
	def drawCard(self, sfdiv, height, page_position, deck, layout=0):
		deckname = deck.get("name")
		faction = deck.get("faction")
		rarities = deck["rarities"]
		spellCount = deck.get("spellCount",0)
		creatureTypes =deck.get("creatureTypes",[])

		div_width = 3.5 * inch
		div_height = height * inch

		left_margin = ((8.5 - (2 * 3.5)) / 2) * inch
		top_margin = ((11 - (height * 3)) / 2 ) * inch

		if page_position == 0:
			row = 2
			col = 1
		else:
			row = ceil(page_position / 2) - 1
			col = page_position % 2
			if col == 0:
				col = 1
			else:
				col = 0

		faction_icon = self.faction_icons.get(faction,"")

		if layout == 0:
			sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
			sfdiv.drawImage(faction_icon, (left_margin - (inch * .4))  + (col * div_width), top_margin + (row * div_height), preserveAspectRatio=True, mask="auto",height=.35*inch)
			sfdiv.setFont("Times-Roman", 12)
			#canvas.setFillColor(red)
			sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14) + top_margin + (row * div_height),deckname)
			sfdiv.setFont("Times-Roman", 8)
			if spellCount > 0:
				sfdiv.drawString((inch * .31) + left_margin + (col * div_width) + (2.7 * inch), (inch * .28) + top_margin + (row * div_height),"Spells: " + str(spellCount))
			rarityCount = 1
			for rarity in rarities:
				sfdiv.drawImage(rarity, (left_margin - (inch * .3)) + (rarityCount * .15 * inch)  + (col * div_width), top_margin + (row * div_height) + (.18* inch), preserveAspectRatio=True, mask="auto",height=.15*inch)
				rarityCount = rarityCount + 1

			creatureCount = 1
			for creature in creatureTypes.keys():
				sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14 * creatureCount) + top_margin + (row * div_height) + (.3* inch),creature + ": " + str(creatureTypes[creature]))
				creatureCount = creatureCount + 1

		elif layout == 1:
			sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
			sfdiv.drawImage(faction_icon, (left_margin - (inch * .4))  + (col * div_width), top_margin + (row * div_height), preserveAspectRatio=True, mask="auto",height=.30*inch)
			sfdiv.setFont("Times-Roman", 11)
			#canvas.setFillColor(red)
			sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14) + top_margin + (row * div_height),deckname)
			sfdiv.setFont("Times-Roman", 8)
			if spellCount > 0:
				sfdiv.drawString((inch * .31) + left_margin + (col * div_width) + (2.7 * inch), (inch * .23) + top_margin + (row * div_height),"Spells: " + str(spellCount))
			rarityCount = 1
			for rarity in rarities:
				sfdiv.drawImage(rarity, (left_margin - (inch * .3)) + (rarityCount * .1 * inch)  + (col * div_width), top_margin + (row * div_height) + (.165* inch), preserveAspectRatio=True, mask="auto",height=.1*inch)
				rarityCount = rarityCount + 1

			creatureCount = 1
			sfdiv.setFont("Times-Roman", 7)
			creatureString = ""
			for creature in sorted(creatureTypes.keys()):
				creatureString = creatureString + " " + creature + ": " + str(creatureTypes[creature])
			
			sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .12 * creatureCount) + top_margin + (row * div_height) + (.215* inch),creatureString)
		elif layout == 2:
			sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
			sfdiv.drawImage(faction_icon, (left_margin - (inch * .4))  + (col * div_width), top_margin + (row * div_height), preserveAspectRatio=True, mask="auto",height=.30*inch)
			sfdiv.setFont("Times-Roman", 11)
			#canvas.setFillColor(red)
			sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14) + top_margin + (row * div_height),deckname)
			sfdiv.setFont("Times-Roman", 8)
			if spellCount > 0:
				sfdiv.drawString((inch * .31) + left_margin + (col * div_width) + (2.7 * inch), (inch * .14) + top_margin + (row * div_height),"Spells: " + str(spellCount))

			creatureCount = 1
			sfdiv.setFont("Times-Roman", 7)
			creatureString = ""
			for creature in sorted(creatureTypes.keys()):
				creatureString = creatureString + " " + creature + ": " + str(creatureTypes[creature])
			
			sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .12 * creatureCount) + top_margin + (row * div_height) + (.15* inch),creatureString)


		if page_position == 0:
			sfdiv.showPage()


	def drawLongLabel(self, sfdiv, height, page_position, deck):
		deckname = deck.get("name")
		faction = deck.get("faction")
		rarities = deck["rarities"]
		spellCount = deck.get("spellCount",0)
		creatureTypes =deck.get("creatureTypes",[])
		creatureNames = deck.get("creatureNames")

		div_width = 3.75 * inch
		div_height = height * inch

		left_margin = ((8.5 - (2 * 3.75)) / 2) * inch
		top_margin = ((11 - (height * 12)) / 2 ) * inch

		if page_position == 0:
			row = 11
			col = 1
		else:
			row = ceil(page_position / 2) - 1
			col = page_position % 2
			if col == 0:
				col = 1
			else:
				col = 0

		faction_icon = self.faction_icons.get(faction,"")

		sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		sfdiv.drawImage(faction_icon, (left_margin - (inch * .4))  + (col * div_width), top_margin + (row * div_height), preserveAspectRatio=True, mask="auto",height=.30*inch)
		sfdiv.setFont("Times-Roman", 11)
		#canvas.setFillColor(red)
		sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14) + top_margin + (row * div_height),deckname)
		sfdiv.setFont("Times-Roman", 8)
		if spellCount > 0:
			sfdiv.drawString((inch * .31) + left_margin + (col * div_width) + (3 * inch), (inch * .25) + top_margin + (row * div_height),"Spells: " + str(spellCount))
		rarityCount = 1
		for rarity in rarities:
			sfdiv.drawImage(rarity, (left_margin - (inch * .3)) + (rarityCount * .1 * inch)  + (col * div_width), top_margin + (row * div_height) + (.165* inch), preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1

		sfdiv.setFont("Times-Roman", 7)
		creatureString = ""
		for creature in sorted(creatureTypes.keys()):
			creatureString = creatureString + "(" + creature + ": " + str(creatureTypes[creature]) + ") "
		
		sfdiv.drawString((inch * .1) + left_margin + (col * div_width), (inch * .12) + top_margin + (row * div_height) + (.25* inch),creatureString)

		creatureNames.sort(key=len)

		creatureNameStringRow1 = "[" + creatureNames[4] + "]" + " [" + creatureNames[6] + "]" + " [" + creatureNames[8] + "]"
		creatureNameStringRow2 = "[" + creatureNames[5] + "]" + " [" + creatureNames[7] + "]" + " [" + creatureNames[9] + "]"
		creatureNameStringRow3 = "[" + creatureNames[0] + "]" + " [" + creatureNames[1] + "]" + " [" + creatureNames[2] + "]" + " [" + creatureNames[3] + "]"

		sfdiv.drawString((inch * .1) + left_margin + (col * div_width), (inch * .12) + top_margin + (row * div_height) + (.355* inch),creatureNameStringRow1)
		sfdiv.drawString((inch * .1) + left_margin + (col * div_width), (inch * .12) + top_margin + (row * div_height) + (.46* inch),creatureNameStringRow2)
		sfdiv.drawString((inch * .1) + left_margin + (col * div_width), (inch * .12) + top_margin + (row * div_height) + (.565* inch),creatureNameStringRow3)

		if page_position == 0:
			sfdiv.showPage()

	def renderLongLabelPDF(self,path,height=.8,sort=0):
		
		try:
			sfdiv = canvas.Canvas(path, pagesize=letter, bottomup=0)
		except IOError:
			print("Cannot save PDF to '%s'." % path)
			
		decksSorted = sorted(self.decks, key=itemgetter('name'))

		if sort == 0:
			decksSorted = sorted(decksSorted, key=itemgetter('faction'))


		deckCount = 0

		for deck in decksSorted:
			deckCount = deckCount + 1

					# 0 Name, rarities, spell cnt - creature counts on body
					# 1 Name, rarities, spell cnt, types
					# 2 Name, spell cnt, types

			self.drawLongLabel(sfdiv,height,deckCount % 24, deck)



		sfdiv.save()

	def renderDividerPDF(self,path,height=2.9,factionDividers=False,sort=0, layout=0):
		
		try:
			sfdiv = canvas.Canvas(path, pagesize=letter, bottomup=0)
		except IOError:
			print("Cannot save PDF to '%s'." % path)
			
		decksSorted = sorted(self.decks, key=itemgetter('name'))

		if sort == 0:
			decksSorted = sorted(decksSorted, key=itemgetter('faction'))


		deckCount = 0

		currentFaction = ""
		factionsBuilt = []

		for deck in decksSorted:
			deckCount = deckCount + 1

			if currentFaction != deck.get("faction") and factionDividers:
				currentFaction = deck.get("faction")
				if currentFaction not in factionsBuilt:
					# 0 Name, rarities, spell cnt - creature counts on body
					# 1 Name, rarities, spell cnt, types
					# 2 Name, spell cnt, types

					self.drawCard(sfdiv,height,deckCount % 6, {
						"name" : currentFaction,
						"faction" : currentFaction,
						"rarities" : [],
						"spellCount" : 0,
						"creatureTypes" : {}
					})
					factionsBuilt.append(currentFaction)
					deckCount = deckCount + 1
			
			self.drawCard(sfdiv,height,deckCount % 6, deck, layout)



		sfdiv.save()


	def drawLabel(self, sfdiv, page_position, deck):

		#67mm x 95.5mm x 22.5mm
		#1 inch * 2.6378
		#.1058 between stickers


		deckname = deck.get("name")
		faction = deck.get("faction")
		rarities = deck["rarities"]
		spellCount = deck.get("spellCount",0)
		creatureTypes =deck.get("creatureTypes",[])
		creatureNames = deck.get("creatureNames")

		div_width = 2.6378 * inch
		div_height = 1 * inch

		left_margin = 0.1875 * inch
		top_margin = .5 * inch

		if page_position == 0:
			row = 9
			col = 0
			box_margin = left_margin + (col * div_width)
		else:
			row = ceil(page_position / 3) - 1
			col = page_position % 3
			if col == 0:
				col = 0
				box_margin = left_margin + (col * div_width)
			else:
				box_margin = left_margin + (col * div_width)+(.1058 * inch * col)

		faction_icon = self.faction_icons.get(faction,"")


#		sfdiv.rect(box_margin, top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		sfdiv.drawImage(faction_icon, (box_margin - (inch * .36)), top_margin + (row * div_height), preserveAspectRatio=True, mask="auto",height=.30*inch)
		sfdiv.setFont("Times-Roman", 11)
		#canvas.setFillColor(red)
		sfdiv.drawString((inch * .3) + box_margin, (inch * .12) + top_margin + (row * div_height),deckname)

		rarityCount = 1
		for rarity in rarities:
			sfdiv.drawImage(rarity, (box_margin - (inch * .26)) + (rarityCount * .1 * inch), top_margin + (row * div_height) + (.185* inch), preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1

		sfdiv.setFont("Times-Roman", 8)
		if spellCount > 0:
			sfdiv.drawString(box_margin + (2.2 * inch), (inch * .10) + top_margin + (row * div_height) + (.15* inch),"Spells: " + str(spellCount))

		creatureCount = 1
		sfdiv.setFont("Times-Roman", 8)
		creatureStringRow1 = ""
		creatureStringRow2 = ""
		for creature in sorted(creatureTypes.keys()):
			if creatureCount < 5:
				creatureStringRow1 = creatureStringRow1 + "(" + creature + ": " + str(creatureTypes[creature]) + ")   "
			else:
				creatureStringRow2 = creatureStringRow2 + "("  + creature + ": " + str(creatureTypes[creature]) + ")   " 

			creatureCount = creatureCount + 1
		
		sfdiv.drawString((inch * .11) + box_margin, (inch * .10) + top_margin + (row * div_height) + (.3* inch),creatureStringRow1)
		sfdiv.drawString((inch * .11) + box_margin, (inch * .10) + top_margin + (row * div_height) + (.42* inch),creatureStringRow2)


		sfdiv.setFont("Times-Roman", 5)

		creatureNames.sort(key=len)

		creatureNameStringRow1 = "[" + creatureNames[4] + "]" + " [" + creatureNames[6] + "]" + " [" + creatureNames[8] + "]"
		creatureNameStringRow2 = "[" + creatureNames[5] + "]" + " [" + creatureNames[7] + "]" + " [" + creatureNames[9] + "]"
		creatureNameStringRow3 = "[" + creatureNames[0] + "]" + " [" + creatureNames[1] + "]" + " [" + creatureNames[2] + "]" + " [" + creatureNames[3] + "]"

		sfdiv.drawString((inch * .11) + box_margin, (inch * .10) + top_margin + (row * div_height) + (.52* inch),creatureNameStringRow1)
		sfdiv.drawString((inch * .11) + box_margin, (inch * .10) + top_margin + (row * div_height) + (.62* inch),creatureNameStringRow2)
		sfdiv.drawString((inch * .11) + box_margin, (inch * .10) + top_margin + (row * div_height) + (.72* inch),creatureNameStringRow3)

		if page_position == 0:
			sfdiv.showPage()

	def refreshStats(self):
		for deck in self.decks:
			cardCount = 0
			spellCount = 0
			creatureTypes = {}
			rarities = []
			creatureNames = []

			while cardCount < 10:
				cardCount = cardCount + 1
				card = deck["cards"][str(cardCount)]
				if card.get("cardType") == "Spell":
					spellCount = spellCount + 1
				if card.get("cardType") == "Creature":
					for subType in card.get("cardSubType","").split(" "):
						if subType in creatureTypes:
							creatureTypes[subType] = creatureTypes[subType] + 1
						else:
							creatureTypes[subType] = 1
				creatureNames.append(card["title"])

				if "crossFaction" in card:
					rarities.append(self.faction_icons.get(card.get("crossFaction"),""))
				if card.get("rarity","") in self.rarity_icons:
					rarities.append(self.rarity_icons[card["rarity"]])

			deck["rarities"] = rarities
			deck["spellCount"] = spellCount
			deck["creatureTypes"] = creatureTypes
			deck["creatureNames"] = creatureNames

		
	def renderLabelPDF(self,path):
		
		try:
			sfdiv = canvas.Canvas(path, pagesize=letter, bottomup=0)
		except IOError:
			print("Cannot save PDF to '%s'." % path)
			
		decksSorted = sorted(self.decks, key=itemgetter('name'))

		decksSorted = sorted(decksSorted, key=itemgetter('faction'))

		deckCount = 0

		#background =  os.path.join(self.resourcePath,"5160.png")
		#sfdiv.drawImage(background,0,11)

		for deck in decksSorted:
			deckCount = deckCount + 1
			
			self.drawLabel(sfdiv,deckCount % 30, deck)


		sfdiv.save()


	def missingImages(self):
		links = []
		for deck in self.decks:
			cards = deck["imageUrl"]
			fbFront = deck["forgeborn"]["imageUrl"]
			fbBack = deck["forgeborn"]["imageUrlBack"]

			if os.path.isfile(os.path.join(self.cacheFolder,cards.rsplit('/', 1)[-1])) == False:
				links.append((cards,os.path.join(self.cacheFolder,cards.rsplit('/', 1)[-1])))
			
			if os.path.isfile(os.path.join(self.cacheFolder,fbFront.rsplit('/', 1)[-1])) == False:
				links.append((fbFront,os.path.join(self.cacheFolder,fbFront.rsplit('/', 1)[-1])))
			
			if os.path.isfile(os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])) == False:
				links.append((fbBack,os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])))
			
		return links

	def parseCardsFromDeckImages(self,outfile, pDialog = None):
		decknumber = 0

		imagePath = os.path.join(outfile, "images")

		Path(imagePath).mkdir(parents=True, exist_ok=True)

		for deck in self.decks:
			if pDialog:
				if pDialog.WasCancelled():
					return
			decknumber = decknumber + 1
			cardIncrement = int((90 / ((len(self.decks) * 12) + 1)) * 100)
			cardnumber = 0
			

			while cardnumber < 10:
				cardnumber = cardnumber + 1
				with Image.open(os.path.join(self.cacheFolder,deck["imageUrl"].rsplit('/', 1)[-1])) as deck_image:
					if pDialog:
						pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cards"][str(cardnumber)]["title"])
					width, height = deck_image.size
					new_left = (cardnumber-1)*(width/10)
					new_right = cardnumber*(width/10)

					levelnumber = 3
					levelPath = 1

					while levelnumber >= 1:
						new_height = levelnumber * (height/3)
						card_image = deck_image.crop((new_left,(height/3) * (levelnumber-1),new_right,new_height))
					
						card_name = deck["name"] + " - " + deck["cards"][str(cardnumber)]["title"] + " - Lvl " +str(levelPath) + ".jpg"

						card_image.save(os.path.join(imagePath,card_name))
						levelnumber = levelnumber - 1
						levelPath = levelPath + 1

			with Image.open(os.path.join(self.cacheFolder,deck["forgeborn"]["imageUrl"].rsplit('/', 1)[-1])) as fb_image:
				if pDialog:
					pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cards"][str(cardnumber)]["title"])

				card_name = deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + ".jpg"
				
				fb_image.save(os.path.join(imagePath,card_name))


			with Image.open(os.path.join(self.cacheFolder,deck["forgeborn"]["imageUrlBack"].rsplit('/', 1)[-1])) as fbBack:
				if pDialog:
					pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cards"][str(cardnumber)]["title"])

				card_name = deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + " Back.jpg"
				
				fbBack.save(os.path.join(imagePath,card_name))

	def generateDeckNavigator(self, out_path, images=False, overview=True):
		template_file = ""

		with open(os.path.join(self.resourcePath,"deck_nav_template.html"), "r") as template_file:
			template = template_file.read()

		Path(os.path.join(out_path,"decks")).mkdir(parents=True, exist_ok=True)

		html = template.split("[deck]")[0]
		index = """<html><body><h2>All Decks</h2><div><p>
		<a href="browse.html">All decks, with filters.</a></p>
		<p><a href="overview.html">All decks, one page summaries.</a></p>
		<p><a href="collection_stats.html">Collection Wide Stats</a></p>
		</div>
		<h2>Single Deck Card Browsers</h2><div>"""
		

		for deck in self.decks:
			index = index + """<p><a href="%s">%s</a> | <a href="https://solforgefusion.com/decks/%s">official</a></p>""" % ("decks/" + deck["name"] + ".html",deck["name"],deck["id"].strip())
			deckHtml = """<html><head>
			<style>
        .long_card {
            display: inline-block;
            position: relative;
			max-width: 80%; 
        }

		.tall_card {
            display: inline-block;
            position: relative;
			max-width: 80%; 
        }
		.slidecontainer {
		width: 100%;
		}

		.slider {
		-webkit-appearance: none;
		width: 100%;
		height: 25px;
		background: #d3d3d3;
		outline: none;
		opacity: 0.7;
		-webkit-transition: .2s;
		transition: opacity .2s;
		}

		.slider:hover {
		opacity: 1;
		}

		.slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 25px;
		height: 25px;
		background: #04AA6D;
		cursor: pointer;
		}

		.slider::-moz-range-thumb {
		width: 25px;
		height: 25px;
		background: #04AA6D;
		cursor: pointer;
		}
		</style>
			</head><body>
			<h1>Adjust Card Size</h1>
<div class="slidecontainer">
  <input type="range" min="1" max="100" value="80" class="slider" id="cardSizer">
  <p>Card Size: <span id="cardSizeSpan"></span></p>
</div>

<script>

(function (scope) {
    // Create a new stylesheet in the bottom
    // of <head>, where the css rules will go
    var style = document.createElement('style');
    document.head.appendChild(style);
    var stylesheet = style.sheet;
    scope.css = function (selector, property, value) {
        // Append the rule (Major browsers)
        try { stylesheet.insertRule(selector+' {'+property+':'+value+'}', stylesheet.cssRules.length);
        } catch(err) {try { stylesheet.addRule(selector, property+':'+value); // (pre IE9)
        } catch(err) {console.log("Couldn't add style");}} // (alien browsers)
    }
})(window);

var slider = document.getElementById("cardSizer");
var output = document.getElementById("cardSizeSpan");
output.innerHTML = slider.value;

slider.oninput = function() {
	css(".tall_card","max-width",this.value.toString() + "%")
	css(".long_card","max-width",this.value.toString() + "%")
  output.innerHTML = this.value;
}
</script>"""
			cards = sorted(deck["cards"].values(), key=itemgetter('cardType'))

			if images:
				imageBlock = """<span class="has-hover-card">
				<img src='data/forge.gif' width='20' height='20'></img>
					<span class="hover-card">
						<img src="%s" width="281" height="206.5"></img>
					</span>
					</span>""" % ("images/" + deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + ".jpg")
			else:
				imageBlock = ""

			factionIcon = os.path.basename(self.faction_icons[deck["faction"]])

			html = html + """<tr>
										<td class = "faction">%s</td>
										<td class = "deckname">%s</td>
										<td>%s</td>
										<td>%s</td>
										<td>Forgeborn</td>
										<td></td>
										<td>
										</td>
										<td>
										</td>
										<td>
											<ol>
												<li class='text2'><strong>%s</strong> - %s</li>
												<li class='text3'><strong>%s</strong> - %s</li>
												<li class='text4'><strong>%s</strong> - %s</li>
											</ol>
										</td>
									</tr>""" % ("<img src='data/" + factionIcon +"' width='20' height='20'></img><span style='display: none;'>"+deck["faction"]+"</span>",
												deck["name"],
									"<span style='display: none;'>Forgeborn</span>" + imageBlock,
													deck["forgeborn"]["title"],
													deck["forgeborn"]["a2n"],
													deck["forgeborn"]["a2t"],
													deck["forgeborn"]["a3n"],
													deck["forgeborn"]["a3t"],
													deck["forgeborn"]["a4n"],
													deck["forgeborn"]["a4t"])
			
			deckHtml = deckHtml + """<div class = "forgeborn_front">
										<img src="../images/%s" class="long_card"></img>
									</div>
									<div class = "forgeborn_back">
										<img src="../images/%s" class="tall_card"></img>
									</div>""" % (deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + ".jpg",
												deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + " Back.jpg")

			for card in cards:
				if "crossFaction" in card:
					rarityIcon = "<img src='data/" + os.path.basename(self.faction_icons[card.get("crossFaction","")]) +"' width='20' height='20'></img>"
				else:
					rarityIcon = ""
				
				rarityIcon = rarityIcon + "<img src='data/" + os.path.basename(self.rarity_icons[card.get("rarity","")]) +"' width='20' height='20'></img>"

				if images:
					imageBlock = """<span class="has-hover-card">
										%s
           							<span class="hover-card">
		   								<img src="images/%s" width="206.5" height="281"></img><img src="images-broken/%s" width="206.5" height="281"></img><img src="images/%s"width="206.5" height="281"></img>
           							</span>
        						 </span>""" % (rarityIcon, deck["name"] + " - " + card["title"] + " - Lvl 1.jpg",
								 deck["name"] + " - " + card["title"] + " - Lvl 2.jpg",
								 deck["name"] + " - " + card["title"] + " - Lvl 3.jpg")
				else:
					imageBlock = rarityIcon

				#min-width="336" min-height="240" 

				deckHtml = deckHtml + """<div class = "lvl1">
											<img src="../images/%s" class="tall_card"></img>
										</div>
										<div class = "lvl2">
											<img src="../images/%s" class="tall_card"></img>
										</div>
										<div class = "lvl3">
											<img src="../images/%s" class="tall_card"></img>
										</div>""" % (deck["name"] + " - " + card["title"] + " - Lvl 1.jpg",
									deck["name"] + " - " + card["title"] + " - Lvl 2.jpg",
									deck["name"] + " - " + card["title"] + " - Lvl 3.jpg")

				
				if card["cardType"] == "Creature":
					html = html + """<tr>
					<td class = "faction">%s</td>
					<td class = "deckname">%s</td>
										<td>%s</td>
										<td>%s</td>
										<td>%s</td>
										<td>%s</td>
										<td>
											<ol>
												<li class='attack'>%s</li>
												<li class='attack'>%s</li>
												<li class='attack'>%s</li>
											</ol>
										</td>
										<td>
											<ol>
												<li class='health'>%s</li>
												<li class='health'>%s</li>
												<li class='health'>%s</li>
											</ol>
										</td>
										<td>
											<ol>
												<li class='text1'>%s</li>
												<li class='text2'>%s</li>
												<li class='text3'>%s</li>
											</ol>
										</td>
									</tr>""" % (
										"<img src='data/" + factionIcon + "' width='20' height='20'></img><span style='display: none;'>"+deck["faction"]+"</span>",
												deck["name"],
										"<span style='display: none;'>"+card.get("rarity","")+"</span>" + imageBlock,
													card["title"],
													card["cardType"],
													card["cardSubType"],
													card["levels"]["1"].get("attack",""),
													card["levels"]["2"].get("attack",""),
													card["levels"]["3"].get("attack",""),
													card["levels"]["1"].get("health",""),
													card["levels"]["2"].get("health",""),
													card["levels"]["3"].get("health",""),
													card["levels"]["1"].get("text",""),
													card["levels"]["2"].get("text",""),
													card["levels"]["3"].get("text","")                                            )
				elif card["cardType"] == "Spell":
					html = html + """<tr>
					<td class = "faction">%s</td>
					<td class = "deckname">%s</td>
										<td>%s</td>
										<td>%s</td>
										<td>%s</td>
										<td></td>
										<td>
										</td>
										<td>
										</td>
										<td>
											<ol>
												<li class='text1'>%s</li>
												<li class='text2'>%s</li>
												<li class='text3'>%s</li>
											</ol>
										</td>
									</tr>""" % ("<img src='data/" + factionIcon +"' width='20' height='20'></img><span style='display: none;'>"+deck["faction"]+"</span>",
											deck["name"],
										"<span style='display: none;'>"+card.get("rarity","")+"</span>" + imageBlock,
													card["title"],
													card["cardType"],
													card["levels"]["1"].get("text",""),
													card["levels"]["2"].get("text",""),
													card["levels"]["3"].get("text","")
													)
			deckHtml = deckHtml + "</body></html>"
			with open(os.path.join(out_path,"decks/" + deck["name"] + ".html"), "w") as deck_file:
				deck_file.write(deckHtml)
		
		index=index + "</div></body>"

		with open(os.path.join(out_path,"browse.html"), "w") as deck_navigator_file:
			deck_navigator_file.write(html)
			deck_navigator_file.write(template.split("[deck]")[1])
		with open(os.path.join(out_path,"index.html"), "w") as index_file:
			index_file.write(index)
		if os.path.isdir(os.path.join(out_path,"data")) == False:
			shutil.copytree(self.resourcePath, os.path.join(out_path,"data"),ignore=shutil.ignore_patterns('*.html', '*.ico'))

		if overview:
			self.generateDeckOverview(out_path)
		
		self.halfDeckList(os.path.join(out_path,"decks.csv"))
		self.collectionStats(os.path.join(out_path,"collection_stats.html"))

		

	def halfDeckList(self, out_path):
		with open(out_path, "w") as halfDeckListFile:
			halfDeckListFile.write("Faction\tName\tID\tSpells\tForgeborn\tAbilities\tCreature Types\tCreature Names\n")
			for deck in self.decks:
				deckRow = []
				deckRow.append(deck["faction"])
				deckRow.append(deck["name"])
				deckRow.append(deck["id"])
				deckRow.append(deck["spellCount"])
				deckRow.append(deck["forgeborn"]["title"])
				deckRow.append(",".join([deck["forgeborn"]["a2n"].strip(),deck["forgeborn"]["a3n"].strip(),deck["forgeborn"]["a4n"].strip()]))

				creatureString = ""
				for creature in sorted(deck["creatureTypes"].keys()):
					creatureString = creatureString + " " + creature + ": " + str(deck["creatureTypes"][creature])
				deckRow.append(creatureString)

				deckRow.append(",".join(deck["creatureNames"]))

				halfDeckListFile.write("\t".join(str(item) for item in deckRow) + "\n")

	def collectionStats(self, out_path):
		with open(out_path, "w") as collectionFile:
			all_types = {}
			all_names = {}
			all_fb = {}
			all_fb2_abilities = {}
			all_fb3_abilities = {}
			all_fb4_abilities = {}

			for deck in self.decks:
				all_fb[deck["forgeborn"]["title"]] = all_fb.get(deck["forgeborn"]["title"],0) + 1
				all_fb2_abilities[deck["forgeborn"]["a2n"].strip()] = all_fb2_abilities.get(deck["forgeborn"]["a2n"].strip(),0) + 1
				all_fb3_abilities[deck["forgeborn"]["a3n"].strip()] = all_fb3_abilities.get(deck["forgeborn"]["a3n"].strip(),0) + 1
				all_fb4_abilities[deck["forgeborn"]["a4n"].strip()] = all_fb4_abilities.get(deck["forgeborn"]["a4n"].strip(),0) + 1
				for type in deck["creatureTypes"]:
					all_types[type] = all_types.get(type,0) + deck["creatureTypes"][type]
				for name in deck["creatureNames"]:
					all_names[name] = all_names.get(name,0) + 1
			
			collectionFile.write("<html><body>")


			collectionFile.write("<h2>Creature Types</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>\n")
			for type in all_types:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_types[type]))
			collectionFile.write("</tbody></table>\n")
			
			collectionFile.write("<h2>Card Names</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>")
			for type in all_names:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_names[type]))
			collectionFile.write("</tbody></table>\n")

			collectionFile.write("<h2>Forgeborn</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>")
			for type in all_fb:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_fb[type]))
			collectionFile.write("</tbody></table>\n")

			collectionFile.write("<h2>Level 2 Abillity</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>")
			for type in all_fb2_abilities:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_fb2_abilities[type]))
			collectionFile.write("</tbody></table>\n")

			collectionFile.write("<h2>Level 3 Abillity</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>")
			for type in all_fb3_abilities:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_fb3_abilities[type]))
			collectionFile.write("</tbody></table>\n")

			collectionFile.write("<h2>Level 4 Abillity</h2>\n<table><thead><tr><td></td><td></td></tr></thead><tbody>")
			for type in all_fb4_abilities:
				collectionFile.write("<tr><td>%s</td><td>%i</td></tr>\n" % (type, all_fb4_abilities[type]))
			collectionFile.write("</tbody></table>\n")

			collectionFile.write("</html></body>")


	def generateDeckOverview(self, out_path):
		template_file = ""

		with open(os.path.join(self.resourcePath,"deck_overview_template.html"), "r") as template_file:
			template = template_file.read()

		html = template.split("[decks]")[0]


		for deck in self.decks:

			cards = sorted(deck["cards"].values(), key=itemgetter('cardType'))

			factionIcon = os.path.basename(self.faction_icons[deck["faction"]])
		

			html = html + """
			
			<div id = "forgeborn">
			<p> %s %s - %s</p>
			<ol class = "fb">
				<li class='text2'><strong>%s</strong> - %s</li>
				<li class='text3'><strong>%s</strong> - %s</li>
				<li class='text4'><strong>%s</strong> - %s</li>
			</ol>""" %	("<img src='data/" + factionIcon +"' width='15' height='15'></img>",
					deck["name"],
					deck["forgeborn"]["title"],
					deck["forgeborn"]["a2n"],
					deck["forgeborn"]["a2t"],
					deck["forgeborn"]["a3n"],
					deck["forgeborn"]["a3t"],
					deck["forgeborn"]["a4n"],
					deck["forgeborn"]["a4t"])


			html = html + "</div>"
			creatureTable = "<table>"
			spellTable = "<table>"

			for card in cards:
				if "crossFaction" in card:
					rarityIcon = "<img src='data/" + os.path.basename(self.faction_icons[card.get("crossFaction","")]) +"' width='20' height='20'></img>"
				else:
					rarityIcon = ""
				

				rarityIcon = rarityIcon + "<img src='data/" + os.path.basename(self.rarity_icons[card.get("rarity","")]) +"' width='20' height='20'></img>"

				if card["cardType"] == "Creature":
					creatureTable = creatureTable + """<tr>
										<td>%s %s<br>%s</td>
										<td>
											<ol>
												<li class='attack'>%s</li>
												<li class='attack'>%s</li>
												<li class='attack'>%s</li>
											</ol>
										</td>
										<td>
											<ol>
												<li class='health'>%s</li>
												<li class='health'>%s</li>
												<li class='health'>%s</li>
											</ol>
										</td>
										<td>
											<ol>
												<li class='text1'>%s</li>
												<li class='text2'>%s</li>
												<li class='text3'>%s</li>
											</ol>
										</td>
									</tr>""" % (
										
										rarityIcon,
													card["title"],
													card["cardSubType"],
													card["levels"]["1"].get("attack",""),
													card["levels"]["2"].get("attack",""),
													card["levels"]["3"].get("attack",""),
													card["levels"]["1"].get("health",""),
													card["levels"]["2"].get("health",""),
													card["levels"]["3"].get("health",""),
													card["levels"]["1"].get("text",""),
													card["levels"]["2"].get("text",""),
													card["levels"]["3"].get("text","")
									)
				
				elif card["cardType"] == "Spell":
					spellTable = spellTable + """<tr>
										<td>%s %s</td>
										<td>
											<ol>
												<li class='text1'>%s</li>
												<li class='text2'>%s</li>
												<li class='text3'>%s</li>
											</ol>
										</td>
									</tr>""" % (rarityIcon,
													card["title"],
													card["levels"]["1"].get("text",""),
													card["levels"]["2"].get("text",""),
													card["levels"]["3"].get("text","")
													)
			html = html + creatureTable + "</table>"+ spellTable + "</table><div style='page-break-after: always'></div>"

		with open(os.path.join(out_path,"overview.html"), "w") as deck_navigator_file:
			deck_navigator_file.write(html)
			deck_navigator_file.write(template.split("[decks]")[1])