import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

result = requests.get("https://pokemondb.net/pokedex/all")
src = result.content

soup = BeautifulSoup(src, "lxml")
divisions = soup.body.main.find_all("div")
main_division = divisions[1].div.find_all("div")
rows = main_division[1].table.tbody

no = []
name = []
links = []
type1 = []
type2 = []
bst = []
hp = []
attack = []
defense = []
sp_attack = []
sp_defense = []
speed = []

for row in rows.find_all("tr"):
    data = row.find_all("td")
    # no.
    span = data[0].find_all("span")
    no.append(span[2].getText())
    # links
    links.append(data[1].a['href'])
    # name
    if data[1].small:
        name.append(data[1].small.getText())
    else:
        name.append(data[1].a.getText())
    # type1
    types = data[2].find_all("a")
    type1.append(types[0].getText())
    # type2
    try:
        type2.append(types[1].getText())
    except IndexError:
        type2.append(" ")
    # bst
    bst.append(data[3].getText())
    # hp
    hp.append(data[4].getText())
    # attack
    attack.append(data[5].getText())
    # defense
    defense.append(data[6].getText())
    # sp_attack
    sp_attack.append(data[7].getText())
    # sp_defense
    sp_defense.append(data[8].getText())
    # speed
    speed.append(data[9].getText())
df = pd.DataFrame(list(zip(no, name, type1, type2, bst, hp, attack, defense, sp_attack, sp_defense, speed)),
                  columns=['no', 'name', 'type1', 'type2', 'bst', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense',
                           'speed'])
for i in range(0, len(links)):
    another_form = 0
    link = links[i]
    if i > 1:
        past_link = links[i - 1]
    if link == past_link:
        another_form += 1
    link = "https://pokemondb.net" + link

    result = requests.get(link)
    src = result.content

    soup = BeautifulSoup(src, "lxml")
    divisions = soup.body.main.find_all("div")

    # generation
    text = divisions[1].p.abbr.getText()
    text = re.search(r"(\d)$", text)
    print(text.group(1))
    box = divisions[5].find_all("div")[1]
    table1 = box.div.div.find_all("div")[1]
    rows = table1.table.tbody.find_all("tr")

    # species
    print(rows[2].td.getText())
    text = rows[3].td.getText()
    text = re.sub(r"\w*\s\([\d′″]*\)$", "", text)
    # size
    print(text)
    text = rows[4].td.getText()
    # print(text)
    text = re.sub(r"\w*\s\([\d.\s\w]*\)$", "", text)
    # weight
    print(text)
    text = rows[5].td.find_all("a")
    # abilities
    for i in text:
        print(i.getText())
    table2 = box.div.div.find_all("div")[2]
    tablet1 = table2.div.find_all("div")[0]
    tablet2 = table2.div.find_all("div")[1]
    data = tablet1.table.tbody.find_all("tr")
    text = data[1].td.getText()
    text = re.sub(r"\([\d.%\s\w,]*\)", "", text)
    # catch rate
    print(text)
    text = data[2].td.getText()
    text = re.sub(r"\([\d.%\s\w,]*\)", "", text)
    # base friendship
    print(text)
    data = tablet2.table.tbody.find_all("tr")
    text = data[1].td.getText()
    # print(text)
    text = re.search(r"^([\d.]*)", text)
    # percent male
    print(text.group(1))
    text = data[2].td.getText()
    text = re.search(r"([\d,]*)[\sa-z]*\)$", text)
    print(text.group(1))
