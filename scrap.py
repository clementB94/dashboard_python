import urllib.request
from html.parser import HTMLParser
from urllib.error import HTTPError
import pandas as pd
import re
import csv

class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.getvalue = False
        self.data = []
        self.row = []
        self.infos = []
        super().__init__()
    def handle_starttag(self, tag, attrs):
        if (len(attrs) == 3):
            # Rang
            if (attrs[0][1].startswith("event-result-row")):
                #Reini la ligne
                self.row = []
                #Ajout du rang
                self.row.append(attrs[0][1].split("-")[-1])
                self.getvalue = True
    def handle_data(self, data):
        if (self.getvalue) :
            self.row.append(data)
            if len(self.row) > 5 : #On a récuperé les infos importantes
                self.getvalue = False
                #On ne prend en compte les données si on a un resultat incorrect
                if 'Notes:' not in self.row:
                    #Gender, Event, Location, Année, Rang, Nom, Pays, Resultat
                    self.save_row()
    def save_row(self):
        final_row = self.infos.copy()
        final_row.append(self.row[0])  #Rank
        final_row.append(self.row[3])  #Name
        final_row.append(self.row[2])  #Country
        result = self.row[5]
        #Format correct : 1:01:01.01
        if not re.match('(\d+):(\d+):(\d+\.\d+)$', result):
            # print("before",result)
            #format 1h01:01
            if re.match('(\d+)h(\d+):(\d+)', result):
                result = re.sub("(\d+)h(\d+):(\d+)", "\\1:\\2:\\3", result)
            #format 1:01.01
            elif re.match('(\d+):(\d+)', result):
                result = re.sub("(\d+):(\d+)", "0:\\1:\\2", result)
            #format 1.01
            elif re.match('(\d+\.\d+)', result):
                result = re.sub("(\d+\.\d+)", "0:00:\\1", result)
            else: return
            # format (pas de texte après le temps)
            if not re.match('(\d+:\d+:\d+\.?\d*)$', result):
                result = re.sub("(\d+:\d+:\d+\.?\d*)(.*)", "\\1", result)
            #FORMATTAGE (1:1:1.10 -> 1:01:1.10)
            splitr = result.split(":")
            result = "{}:{:02d}:{}".format(splitr[0],int(splitr[1]),splitr[2])
            
            
        
            
        final_row.append(result)

        self.data.append(final_row)

    def scan(self, data, game, sport):
        sportSplitted = sport.split("-")
        self.infos = []
        self.infos.append("W" if sportSplitted[-1] == "women" else "M") #Gender
        self.infos.append(" ".join(sportSplitted[0:-1])) #Sport
        gameSplitted = game.split("-")
        self.infos.append(" ".join(gameSplitted[0:-1])) #Location
        self.infos.append(gameSplitted[-1]) #Year
        self.feed(data)
    
summerGames = ['rio-2016', 'london-2012', 'beijing-2008', 'athens-2004', 'sydney-2000', 'atlanta-1996',
            'barcelona-1992', 'seoul-1988', 'los-angeles-1984', 'moscow-1980', 'montreal-1976', 'munich-1972',
            'mexico-city-1968', 'tokyo-1964', 'rome-1960', 'melbourne-1956', 'helsinki-1952', 'london-1948', 'berlin-1936'
            ,'los-angeles-1932','amsterdam-1928','paris-1924','antwerp-1920','stockholm-1912','london-1908','st-louis-1904','paris-1900','athens-1896']

#Basé sur rio2016
sportsRunning = ['100m-men', '100m-women', '200m-men', '200m-women', '400m-men', '400m-women', '800m-men', '800m-women',
                '110m-hurdles-men', '100m-hurdles-women', '400m-hurdles-men', '400m-hurdles-women', '1500m-men', '1500m-women',
                '5000m-men','5000m-women','10000m-men','10000m-women','marathon-men','marathon-women']


fields = ["gender", "sport", "location", "year", "rank", "name", "country","results"]


parser = MyHTMLParser()
for game in summerGames:
    for sport in sportsRunning:
        try:
            url = 'https://olympics.com/en/olympic-games/' + game + '/results/athletics/' + sport
            u = urllib.request.urlopen(url)
            data = u.read().decode('utf8')
            parser.scan(data,game,sport)
        except HTTPError:
            print(game, sport, "introuvable")

print(parser.data)

#TODO : Est-ce que ça ne serait pas mieux d'écrire au fur et a mesure (pas besoin de stocker de liste parser.data) ?
with open('running_times.csv', 'w', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(parser.data)