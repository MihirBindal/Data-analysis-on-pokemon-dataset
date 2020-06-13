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
    links.append("https://pokemondb.net" + data[1].a['href'])
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
        type2.append("None")
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
df = pd.DataFrame(list(zip(no, links, name, type1, type2, bst, hp, attack, defense, sp_attack, sp_defense, speed)),
                  columns=['National Dex no.', 'PokemonDB link', 'Name', 'Primary Type', 'Secondary Type', 'Base Stats Total', 'HP', 'Attack', 'Defense', 'Special Attack',
                           'Special Defense', 'Speed'])
df2 = pd.DataFrame()
generation = []
species = []
size = []
weight = []
abilities = []
catch_rate = []
base_happiness = []
egg_steps = []
percent_male = []
another_form = 0
for i in range(0, len(df['PokemonDB link'])):
    link = df['PokemonDB link'][i]
    if i > 1:
        past_link = links[i - 1]
    else:
        past_link = ""
    if link == past_link:
        another_form += 1
    else:
        another_form = 0
    result = requests.get(link)
    print(link)
    src = result.content
    soup = BeautifulSoup(src, "lxml")
    divisions = soup.body.main.find_all("div")
    # generation
    text = divisions[1].p.abbr.getText()
    text = re.search(r"(\d)$", text)
    generation.append(text.group(1))
    boxes = divisions[5].find_all("div")[1]
    if boxes.div.find_next_sibling("div") is None:
        box_active = boxes.find("div")
    elif another_form == 0:
        box_active = boxes.find("div")
    else:
        box_active = boxes.div.find_next_siblings("div")[another_form - 1]
    table1 = box_active.div.find_all("div")[1]

    rows = table1.table.tbody.find_all("tr")
    # species
    species.append(rows[2].td.getText())
    text = rows[3].td.getText()
    text = re.sub(r"\w*\s\([\d′″]*\)$", "", text)
    # size
    size.append(float(text))
    text = rows[4].td.getText()
    text = re.sub(r"\w*\s\([\d.\s\w]*\)$", "", text)
    # weight
    if text == "—":
        weight.append(" ")
    else:
        weight.append(float(text))
    text = rows[5].td.find_all("a")
    # abilities
    local_list = []
    for i in text:
        local_list.append(i.getText())
    abilities.append(local_list)
    table2 = box_active.div.find_all("div")[2]
    tablet1 = table2.div.find_all("div")[0]
    tablet2 = table2.div.find_all("div")[1]
    data = tablet1.table.tbody.find_all("tr")
    text = data[1].td.getText()
    text = re.sub(r"\([\d.%\s\w,]*\)", "", text)
    # catch rate
    if text == "—":
        catch_rate.append(" ")
    else:
        catch_rate.append(text)
    text = data[2].td.getText()
    text = re.sub(r"\([\d.%\s\w,]*\)", "", text)
    # base friendship
    if text == "—":
        base_happiness.append(" ")
    else:
        base_happiness.append(text)
    data = tablet2.table.tbody.find_all("tr")
    text = data[1].td.getText()
    text = re.search(r"^([\d.]*)", text)
    percent_male.append(text.group(1))
    text = data[2].td.getText()
    text = re.search(r"([,\d]*)[a-z\s]*\)$", text)
    if text is None:
        egg_steps.append("NA")
    else:
        egg_steps.append(text.group(1))

    weakness1 = box_active.find_all('div')[18].find_all("table")[0].find_all("tr")[1].find_all("td")
    weakness2 = box_active.find_all('div')[18].find_all("table")[1].find_all("tr")[1].find_all("td")
    li = []
    for i in range(0, 9):
        temp = weakness1[i].getText()
        if temp == '½':
            temp = 0.5
        elif temp == '':
            temp = 1
        elif temp == '¼':
            temp = 0.25
        elif temp == '1½':
            temp = 1.5
        elif temp == '&frac18;':
            temp = 0.125
        li.append(float(temp))
    for i in range(0, 9):
        temp = weakness2[i].getText()
        if temp == '½':
            temp = 0.5
        elif temp == '':
            temp = 1
        elif temp == '¼':
            temp = 0.25
        elif temp == '1½':
            temp = 1.5
        elif temp == '&frac18;':
            temp = 0.125
        li.append(float(temp))
    col = ["against_normal", "against_fire", "against_water", "against_electric", "against_grass",
           "against_ice", "against_fighting", "against_poison", "against_ground", "against_flying",
           "against_psychic", "against_bug", "against_rock", "against_ghost", "against_dragon",
           "against_dark", "against_steel", "against_fairy"]
    append_dict = dict(zip(col, li))
    df2 = df2.append(append_dict, li)
df3 = pd.DataFrame(list(zip(generation, species, size, weight, abilities, catch_rate, base_happiness, egg_steps)),
                   columns=['Generation', 'Species', 'Size (in metres)', 'Weight (in kgs)', 'Abilities', 'catch rate', 'base happiness',
                            'egg steps'])
final_data = pd.concat([df, df2, df3], axis=1)
final_data = final_data.drop(1028)
final_data.to_csv("pokemon_data_new.csv")
