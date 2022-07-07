SFFToolKit is an application to support the card game <a href="https://solforgefusion.com/">SolForge Fusion</a> by <a href="https://www.stoneblade.com/">Stoneblade Entertainment</a>. It is unaffiliated, unendorsed, and entirely unofficial. It relies on publicly accessible APIs that may or may not continue to work.

Features:
- Create dividers for oganizing your deck collection. The dividers contain the name of the deck, the rarity icons for all cards in the deck, and the number of spells in the deck.
- Sort dividers by faction, then alphabetically by deck name or by deck name only
- include faction dividers
- adjust height of the divider (it assumes horizontal), depending on how tall your box is you may lose the rarity icon row. I wouldn't go lower then 2.9 to get the best results.
- extract card images from the card montage used by TTS, currently just divides it into sets of levels of each card
- generate a local html/js file of all your decks/cards with stats/abilities that can be filtered and searched

Known issues:
- If you provide a filename without a .pdf, it will overwrite a file without warning. If you include the .pdf in the save dialog, it will ask first.
- Things go badly if you say you want faction separators but don’t sort by faction
- The initial download of images the first time doesn't have great feedback that its working. This can be a while if --you have a lot of decks (mine is 100MB of images and takes a quick minute or two).

To do:
- No way to delete a deck
- Checkboxes currently serve no purpose - have them dictate which decks are included in the job and to delete decks
- Provide options for configuring deck navigator
- Create single card images and 3 up horizontally
- Import json from local source
- do we want to put something on body of divider? No

I haven’t done GUI development in over a decade, and used this project as an excuse to learn how to do it in a cross platform way with python (in a previous life I was rather proficient in Obj-C/Cocoa but nowadays I mostly do backend stuff and in python). So its a mix of coding conventions and i'll try to get around to normalizing it at some point. Since its wxWidgets based it might be best to use their naming conventions, but thats going to be a bit of an adjustment for me.

You can run the app from source by installing the dependencies and running python ssftk.py (or python3 if your python command is 2).

Credits:
- reportlab https://www.reportlab.com/opensource/
- requests https://requests.readthedocs.io/en/latest/
- wxWidgets https://wxwidgets.org/about/licence/
- wxPython https://wxpython.org/
- appdirs  https://github.com/ActiveState/appdirs
- Stoneblade https://www.stoneblade.com
- Icon base ToolBox from Vector.me https://Vector.me
- Symbols/Artwork/SFF Logo https://www.stoneblade.com
