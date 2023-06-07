import json
import os
import csv
from appdirs import user_data_dir
from pathlib import Path
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from PIL import Image
from PIL import ImageChops

import shutil
import sys

from operator import itemgetter

def matchScore(item):
  return item["score"]

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

		self.sleeved_box = os.path.join(self.resourcePath,"box_sleeved.png")
		self.unsleeved_box = os.path.join(self.resourcePath,"box_unsleeved.png")

		self.rarity_icons = {

			"s0-Common" : os.path.join(self.resourcePath,"S0_Common.png"),
			"s0-Common Common" : os.path.join(self.resourcePath,"S0_CommonCommon.png"),
			"s0-Common Rare" : os.path.join(self.resourcePath,"S0_CommonRare.png"),
			"s0-Rare" : os.path.join(self.resourcePath,"S0_Rare.png"),
			"s0-Rare Rare" : os.path.join(self.resourcePath,"S0_RareRare.png"),
			"s0-Rare Common" : os.path.join(self.resourcePath,"S0_RareCommon.png"),
			"s0-LS" : os.path.join(self.resourcePath,"S0_LS.png"),
			"s0-Solbind" : os.path.join(self.resourcePath,"S0_LS.png"),
			"s1-Common" : os.path.join(self.resourcePath,"S1_Common.png"),
			"s1-Common Common" : os.path.join(self.resourcePath,"S1_CommonCommon.png"),
			"s1-Common Rare" : os.path.join(self.resourcePath,"S1_CommonRare.png"),
			"s1-Rare" : os.path.join(self.resourcePath,"S1_Rare.png"),
			"s1-Rare Rare" : os.path.join(self.resourcePath,"S1_RareRare.png"),
			"s1-Rare Common" : os.path.join(self.resourcePath,"S1_RareCommon.png"),
			"s1-LS" : os.path.join(self.resourcePath,"S1_LS.png"),
			"s1-Solbind" : os.path.join(self.resourcePath,"S1_LS.png"),
			"s2-Common" : os.path.join(self.resourcePath,"S2_Common.png"),
			"s2-Common Common" : os.path.join(self.resourcePath,"S2_CommonCommon.png"),
			"s2-Common Rare" : os.path.join(self.resourcePath,"S2_CommonRare.png"),
			"s2-Rare" : os.path.join(self.resourcePath,"S2_Rare.png"),
			"s2-Rare Rare" : os.path.join(self.resourcePath,"S2_RareRare.png"),
			"s2-Rare Common" : os.path.join(self.resourcePath,"S2_RareCommon.png"),
			"s2-LS" : os.path.join(self.resourcePath,"S2_LS.png"),
			"s2-Solbind" : os.path.join(self.resourcePath,"S2_Solbind.png"),
			"SX-Missing" : os.path.join(self.resourcePath,"SX_Missing.png")
		}

		self.set_identification_chunks = {

			"ks" : os.path.join(self.resourcePath,"set_kickstarter.jpg"),
			"alpha" : os.path.join(self.resourcePath,"set_alpha.jpg"),
			"wfp" : os.path.join(self.resourcePath,"set_wfp.jpg")
		}

		#load decks from cache
		self.deckNames = []
		self.decks = self.loadCachedDecks()
		self.refreshStats()
		self.scoreLabels = []

	def getRarityIconForSet(self,rarity,set):
		lookup = set + "-" + rarity
		if lookup in self.rarity_icons:
			return self.rarity_icons[lookup]

		return self.rarity_icons["SX-Missing"]


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
		if jsonData.get("id","") == "":
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


	def drawCardBox(self, card_boxes, deck, sleeved):
		deckname = deck.get("name")
		faction = deck.get("faction")
		rarities = deck["rarities"]
		spellCount = deck.get("spellCount",0)
		creatureTypes =deck.get("creatureTypes",[])
		creatureNames = deck.get("creatureNames")


		faction_icon = self.faction_icons.get(faction,"")
		if sleeved == 0:
			box_template = self.unsleeved_box
			left_margin = 5.5 * inch
			top_margin = 1.88 * inch
		else:
			box_template = self.sleeved_box
			left_margin = 5.75 * inch
			top_margin = 1.48 * inch

		card_boxes.drawImage(box_template, 0,0)


		card_boxes.saveState()
		card_boxes.scale(1,-1)

		card_boxes.drawImage(faction_icon, left_margin - (.1 * inch), (top_margin + (.5 * inch)) * -1, preserveAspectRatio=True, mask="auto",height=.35*inch)

		rarityCount = 1
		for rarity in rarities:
			card_boxes.drawImage(rarity, left_margin + (rarityCount * .1 * inch), (top_margin + (.38* inch)) * -1, preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1
		card_boxes.restoreState()
		
		#		sfdiv.rect(box_margin, top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		card_boxes.setFont("Times-Roman", 10)
		#canvas.setFillColor(red)
		card_boxes.drawString((inch * .62) + left_margin, (inch * .24) + top_margin,deckname)

		card_boxes.setFont("Times-Roman", 8)
		if spellCount > 0:
			card_boxes.drawString(left_margin + (2.3 * inch), (inch * .38) + top_margin,"Spells: " + str(spellCount))

		card_boxes.setFont("Times-Roman", 6)
		fb_ability_str = " | ".join([deck["forgeborn"]["a2n"].strip(),deck["forgeborn"]["a3n"].strip(),deck["forgeborn"]["a4n"].strip()])
		fb_ability_str = fb_ability_str.replace("Army of the Damned", "AOTD")
		fb_ability_str = fb_ability_str.replace("the", "")
		card_boxes.drawString(left_margin + (.62* inch), (inch * .50) + top_margin,fb_ability_str)

		creatureCount = 1
		card_boxes.setFont("Times-Roman", 8)
		creatureStringRow1 = ""
		creatureStringRow2 = ""
		for creature in sorted(creatureTypes.keys()):
			if creatureCount < 5:
				creatureStringRow1 = creatureStringRow1 + "(" + creature + ": " + str(creatureTypes[creature]) + ")   "
			else:
				creatureStringRow2 = creatureStringRow2 + "("  + creature + ": " + str(creatureTypes[creature]) + ")   " 

			creatureCount = creatureCount + 1



		if sleeved == 0:
			box_template = self.unsleeved_box
			left_margin = 5.5 * inch
			top_margin = 1.88 * inch
			face_start = .55

		else:
			box_template = self.sleeved_box
			left_margin = 5.75 * inch
			top_margin = 1.48 * inch
			face_start = .88

			card_boxes.setFont("Times-Roman", 5)

			creatureNames.sort(key=len)

			creatureNameStringRow1 = "[" + creatureNames[4] + "]" + " [" + creatureNames[6] + "]" + " [" + creatureNames[8] + "]"
			creatureNameStringRow2 = "[" + creatureNames[5] + "]" + " [" + creatureNames[7] + "]" + " [" + creatureNames[9] + "]"
			creatureNameStringRow3 = "[" + creatureNames[0] + "]" + " [" + creatureNames[1] + "]" + " [" + creatureNames[2] + "]" + " [" + creatureNames[3] + "]"

			card_boxes.drawString((inch * .34) + left_margin, (inch * .65) + top_margin,creatureNameStringRow1)
			card_boxes.drawString((inch * .34) + left_margin, (inch * .73) + top_margin,creatureNameStringRow2)
			card_boxes.drawString((inch * .34) + left_margin, (inch * .81) + top_margin,creatureNameStringRow3)


		card_boxes.setFont("Times-Roman", 8)
		cardCount = 0
		cardType = ""

		for card in sorted(deck.get("cardList"), key=lambda x: x['cardType']):
			if cardType != card['cardType']:
				cardCount = cardCount + 1
				card_boxes.setFillColorRGB(0,0,255)
				card_boxes.drawString((inch * .34) + left_margin, (inch * (face_start + (cardCount * .2))) + top_margin,card['cardType'] + ":")
				cardType = card['cardType']
				card_boxes.setFillColorRGB(0,0,0)


			cardCount = cardCount + 1
			subType = card.get("cardSubType","")
			if subType == "None" or subType == "0" or subType == "":
				subType = ""
			else:
				subType = " - " + subType

			card_boxes.drawString((inch * .34) + left_margin, (inch * (face_start + (cardCount * .2))) + top_margin,"%s%s" % (card.get("name"), subType))

		card_boxes.drawString((inch * .34) + left_margin, (inch * (face_start + ((cardCount + 2) * .2))) + top_margin,creatureStringRow1)
		card_boxes.drawString((inch * .34) + left_margin, (inch * (face_start + ((cardCount + 3) * .2))) + top_margin,creatureStringRow2)
		card_boxes.showPage()


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


		sfdiv.saveState()
		sfdiv.scale(1,-1)
		sfdiv.drawImage(faction_icon, (left_margin - (inch * .4))  + (col * div_width), (top_margin + (.3* inch) + (row * div_height)) * -1, preserveAspectRatio=True, mask="auto",height=.30*inch)
		rarityCount = 1
		for rarity in rarities:
			sfdiv.drawImage(rarity, (left_margin - (inch * .3)) + (rarityCount * .1 * inch)  + (col * div_width), (top_margin + (.115 * inch) + (row * div_height) + (.165* inch)) * -1, preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1
		sfdiv.restoreState()


		sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		sfdiv.setFont("Times-Roman", 11)
		#canvas.setFillColor(red)
		sfdiv.drawString((inch * .3) + left_margin + (col * div_width), (inch * .14) + top_margin + (row * div_height),deckname)
		sfdiv.setFont("Times-Roman", 8)
		if spellCount > 0:
			sfdiv.drawString((inch * .31) + left_margin + (col * div_width) + (3 * inch), (inch * .25) + top_margin + (row * div_height),"Spells: " + str(spellCount))
		

		


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

		sfdiv.setFont("Times-Roman", 6)
		fb_ability_str = " | ".join([deck["forgeborn"]["a2n"].strip(),deck["forgeborn"]["a3n"].strip(),deck["forgeborn"]["a4n"].strip()])
		fb_ability_str = fb_ability_str.replace("Army of the Damned", "AOTD")
		fb_ability_str = fb_ability_str.replace("the", "")
		sfdiv.drawString((inch * .305) + left_margin + (col * div_width) + (1.125 * inch), (inch * .25) + top_margin + (row * div_height),fb_ability_str)


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


	def drawCardBoxes(self,path,sleeved):
		
		try:
			card_boxes = canvas.Canvas(path,pagesize=landscape(letter), bottomup=0)
		except IOError:
			print("Cannot save PDF to '%s'." % path)
			
		decksSorted = sorted(self.decks, key=itemgetter('name'))

		deckCount = 0


		for deck in decksSorted:
			deckCount = deckCount + 1
			self.drawCardBox(card_boxes,deck,sleeved)



		card_boxes.save()

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

		sfdiv.saveState()
		sfdiv.scale(1,-1)
		sfdiv.drawImage(faction_icon, (box_margin - (inch * .36)), top_margin - (1.3*inch) + (row * div_height) * -1, preserveAspectRatio=True, mask="auto",height=.30*inch)

		rarityCount = 1
		for rarity in rarities:
			sfdiv.drawImage(rarity, (box_margin - (inch * .26)) + (rarityCount * .1 * inch), (top_margin + (.265* inch) + (row * div_height)) * -1, preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1
		sfdiv.restoreState()

#		sfdiv.rect(box_margin, top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		sfdiv.setFont("Times-Roman", 11)
		#canvas.setFillColor(red)
		sfdiv.drawString((inch * .3) + box_margin, (inch * .12) + top_margin + (row * div_height),deckname)



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

	def drawLabelUnsleeved(self, sfdiv, page_position, deck):

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
		div_height = .55 * inch

		left_margin = 0.2875 * inch
		top_margin = .28 * inch

		if page_position == 0:
			row = 18
			col = 0
			box_margin = left_margin + (col * div_width)
		else:
			row = ceil(page_position / 3) - 1
			col = page_position % 3
			if col == 0:
				col = 0
				box_margin = left_margin + (col * div_width)
			else:
				box_margin = left_margin + (col * div_width)#+(.1058 * inch * col)

		faction_icon = self.faction_icons.get(faction,"")

		
		sfdiv.saveState()
		sfdiv.scale(1,-1)

#		sfdiv.rect(box_margin, top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)
		sfdiv.drawImage(faction_icon, (box_margin - (inch * .36)), (top_margin + (.32*inch) + (row * div_height)) * -1, preserveAspectRatio=True, mask="auto",height=.30*inch)

		rarityCount = 1
		for rarity in rarities:
			sfdiv.drawImage(rarity, (box_margin - (inch * .26)) + (rarityCount * .1 * inch), (top_margin + (row * div_height) + (.253* inch)) * -1, preserveAspectRatio=True, mask="auto",height=.1*inch)
			rarityCount = rarityCount + 1
		sfdiv.restoreState()
		sfdiv.rect(left_margin + (col * div_width), top_margin + (row * div_height), div_width, div_height, stroke=1, fill=0)

		sfdiv.setFont("Times-Roman", 10)
		#canvas.setFillColor(red)
		sfdiv.drawString((inch * .32) + box_margin, (inch * .12) + top_margin + (row * div_height),deckname)
		sfdiv.setFont("Times-Roman", 8)
		if spellCount > 0:
			sfdiv.drawString(box_margin + (2.12 * inch), (inch * .10) + top_margin + (row * div_height) + (.15* inch),"Spells: " + str(spellCount))
	
		sfdiv.setFont("Times-Roman", 6)
		fb_ability_str = " | ".join([deck["forgeborn"]["a2n"].strip(),deck["forgeborn"]["a3n"].strip(),deck["forgeborn"]["a4n"].strip()])
		fb_ability_str = fb_ability_str.replace("Army of the Damned", "AOTD")
		fb_ability_str = fb_ability_str.replace("the", "")
		sfdiv.drawString((inch * .32) + box_margin, top_margin + (row * div_height) + (.32* inch),fb_ability_str)



		creatureCount = 1
		sfdiv.setFont("Times-Roman", 6)
		creatureStringRow1 = ""
		creatureStringRow2 = ""
		for creature in sorted(creatureTypes.keys()):
			if creatureCount < 5:
				creatureStringRow1 = creatureStringRow1 + "(" + creature + ": " + str(creatureTypes[creature]) + ")   "
			else:
				creatureStringRow2 = creatureStringRow2 + "("  + creature + ": " + str(creatureTypes[creature]) + ")   " 

			creatureCount = creatureCount + 1
		sfdiv.drawString((inch * .05) + box_margin, top_margin + (row * div_height) + (.40* inch),creatureStringRow1)
		sfdiv.drawString((inch * .05) + box_margin, top_margin + (row * div_height) + (.48* inch),creatureStringRow2)

		if page_position == 0:
			sfdiv.showPage()
	# def refreshStats(self):
	# 	for deck in self.decks:
	# 		cardCount = 0
	# 		spellCount = 0
	# 		creatureTypes = {}
	# 		rarities = []
	# 		creatureNames = []

	# 		while cardCount < 10:
	#			cardCount = cardCount + 1
	# 			card = deck["cards"][str(cardCount)]
	# 			if card.get("cardType") == "Spell":
	# 				spellCount = spellCount + 1
	# 			if card.get("cardType") == "Creature":
	# 				for subType in card.get("cardSubType","").split(" "):
	# 					if subType in creatureTypes:
	# 						creatureTypes[subType] = creatureTypes[subType] + 1
	# 					else:
	# 						creatureTypes[subType] = 1
	# 			creatureNames.append(card["name"])

	# 			if "crossFaction" in card:
	# 				rarities.append(self.faction_icons.get(card.get("crossFaction"),""))
	# 			if card.get("rarity","") in self.rarity_icons:
	# 				rarities.append(self.rarity_icons[card["rarity"]])

	# 		deck["rarities"] = rarities
	# 		deck["spellCount"] = spellCount
	# 		deck["creatureTypes"] = creatureTypes
	# 		deck["creatureNames"] = creatureNames

	def deckSimilarityStats(self):
		
		for deck in self.decks:
			cards = {}
			deck["Match Scores"] = []

			for card in deck["cards"]:
				cards[deck["cards"][card]["title"]] = deck["cards"][card].get("spliced",False)
			
			for deckToCompare in self.decks:
				cardsToCompare = {}
				if deckToCompare == deck or deckToCompare["faction"] != deck["faction"]:
					continue
				else:
					for card in deckToCompare["cards"]:
						cardsToCompare[deckToCompare["cards"][card]["title"]] = deckToCompare["cards"][card].get("spliced",False)

				same = list(set(cards.keys()).intersection(cardsToCompare.keys()))
				diff = list(set(cards.keys()).difference(cardsToCompare.keys()))
				diff2 = list(set(cardsToCompare.keys()).difference(cards.keys()))
				
				unique = []
				unique.extend(diff)
				unique.extend(diff2)

		
				deck_forged_pieces = []
				deck_to_compare_forged_pieces = []
				for d in unique:

					if d in cards and cards[d] == 'True':
						deck_forged_pieces.extend(d.replace("Charge Plated", "CP").split(" "))
					if d in cardsToCompare and cardsToCompare[d] == 'True':
						deck_to_compare_forged_pieces.extend(d.replace("Charge Plated", "CP").split(" "))

				f_same = list(set(deck_forged_pieces).intersection(deck_to_compare_forged_pieces))

				whole_matches = len(same)
				forged_points = len(f_same) / 2
				cards_total = ((whole_matches + forged_points) / 10) * 100 
				deck["Match Scores"].append({"name": deckToCompare["name"],"score" : cards_total})

			deck["Match Scores"].sort(key=matchScore,reverse=True)


#stats()

	def refreshStats(self):
		for deck in self.decks:
			cardCount = 0
			spellCount = 0
			creatureTypes = {}
			rarities = []
			creatureNames = []
			baseCreatures = []
			modifiers = []

			while cardCount < 10:
				
				card = deck["cardList"][cardCount]
				if card.get("cardType") == "Spell":
					spellCount = spellCount + 1
				if card.get("cardType") == "Creature":
					for subType in card.get("cardSubType","").split(" "):
						if subType in creatureTypes:
							creatureTypes[subType] = creatureTypes[subType] + 1
						else:
							creatureTypes[subType] = 1

				creatureNames.append(card["name"])			
				

				if card.get("betrayer",False):
					rarities.append(self.faction_icons.get(card.get("crossFaction"),""))
				
				rarities.append(self.getRarityIconForSet(card.get("rarity","Missing"),deck.get("cardSetId","SX")))
				cardCount = cardCount + 1


			deck["rarities"] = rarities
			deck["spellCount"] = spellCount
			deck["creatureTypes"] = creatureTypes
			deck["creatureNames"] = creatureNames
			deck["baseCreatures"] = baseCreatures
			deck["modifiers"] = modifiers
		
		self.decks.sort(key=itemgetter('faction', 'name'))

		self.cardScoreRefresh()

		#self.deckSimilarityStats()


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
			
			self.drawLabelUnsleeved(sfdiv,deckCount % 57, deck)


		sfdiv.save()

	def renderLabelPDFSleeved(self,path):
		
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
	def missingFBBacks(self):
		links = []
		for deck in self.decks:
			fbBack = "https://sfwmedia11453-main.s3.amazonaws.com/public/cards/"+deck["id"]+"_fb_back.jpg"
			if os.path.isfile(os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])) == False:
				links.append((fbBack,os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])))
	
		return links
	
	def findKickstarterDecks(self):
		checkImg = Image.open(os.path.join(self.resourcePath,"set_kickstarter.jpg"))
		checkImgb = Image.open(os.path.join(self.resourcePath,"set_kickstarterb.jpg"))
		
		for deck in self.decks:
			if deck["cardSetId"] == "s1":
				with Image.open(os.path.join(self.cacheFolder,deck["id"]+"_fb_back.jpg")) as deck_image:
					cropped_image = deck_image.crop((520,900,610,930))
					cropped_image.save(os.path.join(self.cacheFolder,deck["id"]+"setcheck.jpg"))

					sampleImg = Image.open(os.path.join(self.cacheFolder,deck["id"]+"setcheck.jpg"))


					if not ImageChops.difference(sampleImg, checkImg).getbbox():
						deck["cardSetId"] = "s0"
					elif not ImageChops.difference(sampleImg, checkImgb).getbbox():
						deck["cardSetId"] = "s0"
		self.refreshStats()

	def missingImages(self, incCards=True):
		links = []
		for deck in self.decks:
			fbBack = "https://sfwmedia11453-main.s3.amazonaws.com/public/cards/"+deck["id"]+"_fb_back.jpg"
			fbFront = "https://sfwmedia11453-main.s3.amazonaws.com/public/cards/resized/"+deck["forgebornId"]+".jpg"
			if os.path.isfile(os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])) == False:
				links.append((fbBack,os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])))
			
			if os.path.isfile(os.path.join(self.cacheFolder,fbFront.rsplit('/', 1)[-1])) == False:
				links.append((fbFront,os.path.join(self.cacheFolder,fbFront.rsplit('/', 1)[-1])))
			

			if incCards:
				cards = deck["cardIds"]

				for card in cards:
					if os.path.isfile(os.path.join(self.cacheFolder,card + "_1.jpg")) == False:
						links.append(("https://sfwmedia11453-main.s3.amazonaws.com/public/cards/resized/"+card+"_1.jpg",os.path.join(self.cacheFolder,card + "_1.jpg")))
				for card in cards:
					if os.path.isfile(os.path.join(self.cacheFolder,card + "_2.jpg")) == False:
						links.append(("https://sfwmedia11453-main.s3.amazonaws.com/public/cards/resized/"+card+"_2.jpg",os.path.join(self.cacheFolder,card + "_2.jpg")))

				for card in cards:
					if os.path.isfile(os.path.join(self.cacheFolder,card + "_3.jpg")) == False:
						links.append(("https://sfwmedia11453-main.s3.amazonaws.com/public/cards/resized/"+card+"_3.jpg",os.path.join(self.cacheFolder,card + "_3.jpg")))
			
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
				
				with Image.open(os.path.join(self.cacheFolder,deck["imageUrl"].rsplit('/', 1)[-1])) as deck_image:
					if pDialog:
						pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cardList"][cardnumber]["name"])
					width, height = deck_image.size
					new_left = (cardnumber-1)*(width/10)
					new_right = cardnumber*(width/10)

					levelnumber = 3
					levelPath = 1

					while levelnumber >= 1:
						new_height = levelnumber * (height/3)
						card_image = deck_image.crop((new_left,(height/3) * (levelnumber-1),new_right,new_height))
					
						card_name = deck["name"] + " - " + deck["cardList"][cardnumber]["name"] + " - Lvl " +str(levelPath) + ".jpg"

						card_image.save(os.path.join(imagePath,card_name))
						levelnumber = levelnumber - 1
						levelPath = levelPath + 1
				cardnumber = cardnumber + 1

			with Image.open(os.path.join(self.cacheFolder,deck["forgeborn"]["imageUrl"].rsplit('/', 1)[-1])) as fb_image:
				if pDialog:
					pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cardList"][cardnumber]["name"])

				if "name" in deck["forgeborn"]:
					card_name = deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["name"] + ".jpg"
				else:
					card_name = deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["title"] + ".jpg"

				fb_image.save(os.path.join(imagePath,card_name))


			if "imageUrlBack" in deck["forgeborn"]:
				fbBack = deck["forgeborn"]["imageUrlBack"]
				if os.path.isfile(os.path.join(self.cacheFolder,fbBack.rsplit('/', 1)[-1])) == False:
					with Image.open(fbBack) as fbBack:
						if pDialog:
							pDialog.Update(cardIncrement,newmsg="Extracting " + deck["name"] + " - " + deck["cards"][str(cardnumber)]["name"])

						card_name = deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"]["name"] + " Back.jpg"
						
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
			cards = sorted(deck["cardList"], key=itemgetter('cardType'))

			fb_name = ("images/" + deck["name"] + " - " + "Forgeborn - " + deck["forgeborn"].get("title",deck["forgeborn"].get("name","")) + ".jpg")
			

			if images:
				imageBlock = """<span class="has-hover-card">
				<img src='data/forge.gif' width='20' height='20'></img>
					<span class="hover-card">
						<img src="%s" width="281" height="206.5"></img>
					</span>
					</span>""" % ("images/" + fb_name + ".jpg")
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
													deck["forgeborn"].get("title",deck["forgeborn"].get("name","")),
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
									</div>""" % (deck["forgebornId"] + ".jpg",
												deck["id"] + "_fb_back.jpg")

			for card in cards:
				if "crossFaction" in card:
					rarityIcon = "<img src='data/" + os.path.basename(self.faction_icons[card.get("crossFaction","")]) +"' width='20' height='20'></img>"
				else:
					rarityIcon = ""
				
				rarityIcon = rarityIcon + "<img src='data/" + os.path.basename(self.getRarityIconForSet(card.get("rarity","Missing"),card.get("cardSetId","SX"))) +"' width='20' height='20'></img>"

				if images:
					imageBlock = """<span class="has-hover-card">
										%s
           							<span class="hover-card">
		   								<img src="images/%s" width="206.5" height="281"></img><img src="images-broken/%s" width="206.5" height="281"></img><img src="images/%s"width="206.5" height="281"></img>
           							</span>
        						 </span>""" % (rarityIcon, deck["name"] + " - " + card["name"] + " - Lvl 1.jpg",
								 deck["name"] + " - " + card["name"] + " - Lvl 2.jpg",
								 deck["name"] + " - " + card["name"] + " - Lvl 3.jpg")
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
										</div>""" % (deck["name"] + " - " + card["name"] + " - Lvl 1.jpg",
									deck["name"] + " - " + card["name"] + " - Lvl 2.jpg",
									deck["name"] + " - " + card["name"] + " - Lvl 3.jpg")

				
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
													card["name"],
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
													card["name"],
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
			halfDeckListFile.write("Faction\tName\tID\tDate\tSpells\tForgeborn\tAbilities\tCreature Types\tCreature Names\n")
			for deck in self.decks:
				deckRow = []
				deckRow.append(deck["faction"])
				deckRow.append(deck["name"])
				deckRow.append(deck["id"])
				deckRow.append(deck["registeredDate"])
				deckRow.append(deck["spellCount"])
				deckRow.append(deck["forgeborn"].get("title",deck["forgeborn"].get("name","")))
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
				all_fb[deck["forgeborn"].get("title",deck["forgeborn"].get("name",""))] = all_fb.get(deck["forgeborn"].get("title",deck["forgeborn"].get("name","")),0) + 1
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
			#old location of card data
			#cards = sorted(deck["cards"].values(), key=itemgetter('cardType'))

			cards = sorted(deck["cardList"], key=itemgetter('cardType'))

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
					deck["forgeborn"].get("title",deck["forgeborn"].get("name","")),
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
				if "crossFaction" in card and card.get("betrayer", False):
					rarityIcon = "<img src='data/" + os.path.basename(self.faction_icons[card.get("crossFaction","")]) +"' width='20' height='20'></img>"
				else:
					rarityIcon = ""

				rarityIcon = rarityIcon + "<img src='data/" + os.path.basename(self.getRarityIconForSet(card.get("rarity","Missing"),deck.get("cardSetId","SX"))) +"' width='20' height='20'></img>"

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
													card["name"],
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
													card["name"],
													card["levels"]["1"].get("text",""),
													card["levels"]["2"].get("text",""),
													card["levels"]["3"].get("text","")
													)
			html = html + creatureTable + "</table>"+ spellTable + "</table><div style='page-break-after: always'></div>"
			
			#if deck["Match Scores"][0]["score"] > 57:
			#html = html + deck["Match Scores"][0]["name"] + ":" + str(deck["Match Scores"][0]["score"]) +"</div>"
			#html = html + deck["Match Scores"][1]["name"] + ":" + str(deck["Match Scores"][1]["score"]) +"</div>"
			#html = html + deck["Match Scores"][2]["name"] + ":" + str(deck["Match Scores"][2]["score"]) +"</div>"
			#	print(deck["name"] + " ---> " + deck["Match Scores"][0]["name"] + ":" + str(deck["Match Scores"][0]["score"]) + ", " + deck["Match Scores"][1]["name"] + ":" + str(deck["Match Scores"][1]["score"]) + ", " + deck["Match Scores"][2]["name"] + ":" + str(deck["Match Scores"][2]["score"]))


		with open(os.path.join(out_path,"overview.html"), "w") as deck_navigator_file:
			deck_navigator_file.write(html)
			deck_navigator_file.write(template.split("[decks]")[1])

	def cardScoreRefresh(self):
		scoreLookup = {}
		
		with open(os.path.join(self.resourcePath,"card_scores.csv"), "r") as card_scores:
			all_scores = csv.DictReader(card_scores)
			for score in all_scores:
				scoreLookup[score["id"]] = score
				
		self.scoreLabels = sorted(list(all_scores.fieldnames)[3:])

		for deck in self.decks:
			cardLookupIds = []
			if "scores" not in deck:
				deck["scores"] = {}

			for cardId in deck["cardIds"]:
				if cardId[5:] in scoreLookup:
					cardLookupIds.append(cardId[5:])
					if scoreLookup[cardId[5:]].get("solbind","") != "":
						cardLookupIds.append(scoreLookup[cardId[5:]]["solbind"])
				else:
					unforged = cardId.replace("charge-plated","charge_plated")[5:].split("-")
					cardLookupIds.extend(unforged)
                    #displayName = cardLookup[modifier]["Name"] + " " + cardLookup[basecreature]["Name"];

				if cardId[2] != cardId[3]:
					deck["betrayer"] = cardId
			for cardId in cardLookupIds:
				all_scores = scoreLookup.get(cardId,{})

				for score in list(all_scores.keys())[3:]:
					deck["scores"][score] = deck["scores"].get(score,0) + int(all_scores[score])
		#print(deck)
		#self.allDeckJson("teest.html")
		#exit()


	def allDeckJson(self, out_path):
		faction_color = {
			"Uterra" : "green",
			"Nekrium" : "purple",
			"Alloyin" : "blue",
			"Tempys" : "red",
		}
		template_file = ""
		records = ""

		with open(os.path.join(self.resourcePath,"cm.html"), "r") as template_file:
			template = template_file.read()

		with open(out_path, "w") as collectionFile:
			searches = """[
				{ field: 'name', label: 'Deck Name', type: 'text' },
				{ field: 'cards', label: 'Card List', type: 'text' },
				{
					field: 'faction', label: 'Faction', type: 'enum', style: 'width1: 350px',
					options: { items: ['Alloyin','Nekrium','Tempys','Uterra'] }
				},
				{
					field: 'forgeborn', label: 'Forgeborn', type: 'enum', style: 'width1: 350px',
					options: { items: ['Oros','Nova','Nix','Cercee','Sunder','Korok','Steel Rosetta','Ironbeard','Crux Colbalt'] }
				},
				{ field: 'sdate', label: 'Registered Date', type: 'date' }
			]"""
			columns = """
						[
				{ field: 'name', text: 'Deck Name', size: '256px', sortable: true },
				{ field: 'cards', text: 'Card List', size: '80px', sortable: true },
				{ field: 'fb_cycle_2', text: 'FB Cycle 2', size: '80px' },
				{ field: 'fb_cycle_3', text: 'FB Cycle 3', size: '80px' },
				{ field: 'fb_cycle_4', text: 'FB Cycle 4', size: '80px' },
			"""
			#visibleColumns = """
			#<option value="name">Deck Name</option>
			#<option value="cards">Card List</option>
			#<option value="fb_cycle_2">FB Cycle 2</option>
			#<option value="fb_cycle_3">FB Cycle 3</option>
			#<option value="fb_cycle_4">FB Cycle 4</option>
			#"""
			visibleColumns = "["

			scoreCount = 0
			for score in self.scoreLabels:
				scoreCount = scoreCount + 1
				columns = columns + """{ field: '%s', text: '%s', size: '10px' },""" % (score, score)
				visibleColumns = visibleColumns + """{ "recid": '%i', "name": '%s'},""" % (scoreCount, score)
			columns = columns[:-1] + """]"""
			visibleColumns = visibleColumns[:-1] + """]"""
		

			records = records +"["
			deckCount = 0
			
			for deck in self.decks:
				deckCount = deckCount + 1
				deckRow = "        {"
				deckRow = deckRow + """
				"recid": %i, 
				"id": "%s", 
				"name": "%s", 
				"faction": "%s", 
				"cards": "%s", 
				"forgeborn": "%s",
				"fb_cycle_2": "%s",
				"fb_cycle_3": "%s",
				"fb_cycle_4": "%s",
				"betrayer": "%s",
				"solbind": "%s",
				""" % (deckCount,
				deck["id"],
				deck["name"],
				deck["faction"],
				",".join(deck["creatureNames"]),
				deck["forgeborn"].get("title",deck["forgeborn"].get("name","")),
				deck["forgeborn"]["a2n"],
				deck["forgeborn"]["a3n"],
				deck["forgeborn"]["a4n"],
				deck.get("betrayer",""),
				deck.get("solbind",""))

				for score in self.scoreLabels:
					deckRow = deckRow + """"%s" : %i,""" % (score, deck.get("scores",{}).get(score,""))
				
				deckRow = deckRow +  """w2ui: { style: { name: "color: %s;" }}""" % (faction_color.get(deck["faction"]))

				deckRow = deckRow + "        }"
				if deckCount != len(self.decks):
					deckRow = deckRow + ","
				
				records = records + deckRow
					
			records = records + "]"
			collectionFile.write(template.replace("**COLUMNS**",columns).replace("**RECORDS**",records).replace("**SEARCHES**",searches).replace("**COLRECORDS**",visibleColumns))

		with open(out_path+"fred.txt", "w") as collectionFile:

			
			for deck in self.decks:
				collectionFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (deck["id"],
				deck["name"],
				deck["faction"],
				",".join(deck["creatureNames"]),
				deck["forgeborn"].get("title",deck["forgeborn"].get("name","")),
				deck["forgeborn"]["a2n"],
				deck["forgeborn"]["a3n"],
				deck["forgeborn"]["a4n"],
				deck.get("betrayer",""),
				deck.get("solbind","")))

				for score in self.scoreLabels:
					collectionFile.write("\t%s\t%i" % (score, deck.get("scores",{}).get(score,"")))
				collectionFile.write("\n")