#! /bin/env python3
# Ce programme permet de re-télécharger les fichiers de traduction
# française du jeu Wesnoth depuis la branche master du dépôt GitHub.
# Usage : lancer ce script depuis un emplacement contenant des dossiers
# dont les noms correspondent aux versions du jeu (1.18, 1.16.9, master,
# ...) contenant des fichiers .po aux noms des domaines de traduction. Le
# script va télécharger les fichier PO correspondant et les placer dans
# les dossiers.
# /!\ Ce script écrase votre travail sans confirmation !!!


import os
import concurrent.futures
import requests
import subprocess


class term:
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    CROSS = "\u2718"
    CHECK = "\u2714"


class POFile:
    def __init__(self, tag, domain):
        self.content = None
        self.tag = tag
        self.domain = domain
        self.name = tag + ":" + domain
        self.url = (
            "https://raw.githubusercontent.com/wesnoth/wesnoth/"
            + tag
            + "/po/"
            + domain
            + "/fr.po"
        )

    def __eq__(self, other):
        if str(other) == self.name:
            return True
        return False

    def __repr__(self):
        return self.name

    def download(self):
        print(
            f"Téléchargement de {term.OKCYAN}{self.domain}{term.ENDC} pour la branche {term.OKCYAN}{self.tag}{term.ENDC}…"
        )
        try:
            pofile = requests.get(self.url)
        except:
            raise Warning(
                f"Le téléchargement à échoué pour {term.FAIL}{self.domain}{term.ENDC} sur la branche {term.FAIL}{self.tag}{term.ENDC}"
            )
        if pofile.status_code >= 400:
            raise Warning(
                f"Le téléchargement à échoué pour {term.FAIL}{self.domain}{term.ENDC} sur la branche {term.FAIL}{self.tag}{term.ENDC}"
            )
        self.content = pofile.content
        return True

    def store(self):
        if self.content == None:
            raise Warning(
                f"Veuillez télécharger {self.domain} sur la branche {self.tag} avant de l'enregistrer"
            )
        print(
            f"{term.OKGREEN}{term.CHECK}{term.ENDC} Enregistrement de {term.OKGREEN}{self.tag}/{self.domain}.po{term.ENDC}"
        )
        open(f"{self.tag}/{self.domain}.po", "wb").write(self.content)
        subprocess.run(
            [
                "git",
                "add",
                f"{self.tag}/{self.domain}.po",
            ],
            check=True,
        )
        return True


dirlist = [i for i in os.listdir(".") if os.path.isdir(i) and i[0] != "."]

pofiles = []

for tag in dirlist:
    filelist = [i[:-3] for i in os.listdir(tag) if i[-3:] == ".po"]
    for domain in filelist:
        pofiles.append(POFile(tag, domain))

if len(pofiles) == 0:
    exit(f"{term.FAIL}{term.CROSS}{term.WARNING} Rien à faire, on quitte.{term.ENDC}")


with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_url = {executor.submit(pofile.download): pofile for pofile in pofiles}
    for future in concurrent.futures.as_completed(future_to_url):
        try:
            future.result()
        except Warning as w:
            print(
                f"{term.FAIL}{term.CROSS}{term.WARNING} Un téléchargement a échoué !{term.ENDC}"
            )
            print(w)
        else:
            future_to_url[future].store()

print(f"\n{term.OKCYAN}=== Lancement du formatage automatique ==={term.ENDC}\n")
try:
    subprocess.run(
        [
            "git",
            "hook",
            "run",
            "pre-commit",
        ],
        check=True,
    )
except subprocess.CalledProcessError:
    print(f"\n{term.FAIL}{term.CROSS}{term.WARNING} Le formatage automatique a échoué !{term.ENDC}")
else:
    print(f"\n{term.OKGREEN}{term.CHECK}{term.ENDC} Formatage automatique terminé")
