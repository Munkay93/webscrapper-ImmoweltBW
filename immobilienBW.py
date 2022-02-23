import bs4 as bs
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import os


def filter_num(string: str, swap=False):
    string_new=""
    for i, char in enumerate(string):
        if char.isdigit() or (char in [",","."] and i != len(string)-1):
            if char == "." and swap:
                char = "," 

            string_new = string_new+char

    return string_new


OUTPUT_DIR = "outputs"

try:
    os.mkdir(OUTPUT_DIR)
except:
    print("output directory allready exists")

num_pages = 100
filename = "output"

col_dict = {
     "Titel": "Titel",
     "Standort": "Standort",
     "Grundstücksfläche":"Grundstücksfläche [m²]",
     "Fakten":"Fakten",
     "Preis":"Preis [EUR]",
     "Wohnfläche":"Wohnfläche [m²]",
     "Zimmer":"Zimmer",
     "Zeit":"Bezugsfertig",
     "num_Wohnungen": "Anzahl Wohnungen"
    }

# Lade alten Pickle Dataframe
try:
    df = pd.read_pickle(OUTPUT_DIR + filename)
except:
    print("No old Dataframe available. Creating new one")
    df = pd.DataFrame(columns=list(col_dict.values()))

for page in range(1,num_pages):
    print(f"Page: {page}")
    print(f"Einträge: {len(df.index)}")
    url = f"https://www.immowelt.de/liste/bl-baden-wuerttemberg/haeuser/kaufen?d=true&sd=DESC&sf=RELEVANCE&sp={page}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    units = soup.find_all("div", class_=["FactsContainer-73861","FactsMain-bb891"])

    for item in units:

        title = item.find("h2").text
        location = item.find(string="location").next.text

        try:
            sqmArea = item.find(string="home_land_area").next.text
        except:
            sqmArea="NA"

        try:
            facts = item.find(string="check").next.text    
        except:
            facts = "NA"
        
        price = item.find(attrs={"data-test": "price"}).text
        sqmW = item.find(attrs={"data-test": "area"}).text
        num_rooms = item.find(attrs={"data-test": "rooms"}).text
        try:
            time = item.find(string="time").next.text
        except:
            time = "NA"
        try:
            home = item.find(string="home").next.text
        except:
            home = "NA"

        # Einheiten entfernen
        sqmArea = filter_num(sqmArea)
        sqmArea=sqmArea[:-1]
        sqmW = filter_num(sqmW, swap=True)
        sqmW=sqmW[:-1]
        price = filter_num(price)
        num_rooms = filter_num(num_rooms, swap=True)

        serie = {
        col_dict["Titel"]:title,
        col_dict["Standort"]:location,
        col_dict["Grundstücksfläche"]:sqmArea,
        col_dict["Fakten"]:facts,
        col_dict["Preis"]:price,
        col_dict["Wohnfläche"]:sqmW,
        col_dict["Zimmer"]:num_rooms,
        col_dict["Zeit"]:time,
        col_dict["num_Wohnungen"]:home
        }
        serie = pd.Series(serie)

        df.loc[len(df.index)] = serie

df = df.drop_duplicates()
df[col_dict["Preis"]].replace('', np.nan, inplace=True)
df[col_dict["Wohnfläche"]].replace('', np.nan, inplace=True)
df = df.dropna()
df = df.loc[df[col_dict["Preis"]] != 0]
df = df.reset_index(drop=True)


df.to_pickle(os.path.join(OUTPUT_DIR, filename+".pkl"))
df.to_excel(os.path.join(OUTPUT_DIR, filename+".xlsx"))





