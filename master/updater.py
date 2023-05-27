# Ce programme permet de re-télécharger les fichiers de traduction française
# du jeu Wesnoth depuis la branche master du dépôt GitHub.
# Usage : lancer ce script depuis un dossier contenant des dossiers
# dont les noms correspondent aux domaines de traduction. Le script va télécharger
# les fichier PO correspondant et les placer dans les dossiers.
# /!\ Ce script écrase votre travail sans confirmation !!!

import os
import requests

path = os.path.split(os.path.abspath(__file__))[0] + "/"

filelist = [i for i in os.listdir(path) if not "." in i]

for i in filelist:
    url = (
        "https://raw.githubusercontent.com/wesnoth/wesnoth/master/po/"
        + i
        + "/fr.po"
    )
    pofile = requests.get(url)
    if pofile.status_code != 404:
        open(path + i + "/fr.po", "wb").write(pofile.content)
