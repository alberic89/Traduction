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
    open(path + i + "/fr.po", "wb").write(pofile.content)
