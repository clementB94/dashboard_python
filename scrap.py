import urllib.request
from abc import ABC
from html.parser import HTMLParser
from urllib.error import HTTPError
import re
import csv


class MyHTMLParser(HTMLParser, ABC):
    def __init__(self, resultAsTime=False):
        self.resultAsTime = resultAsTime
        self.getvalue = False
        self.data = []
        self.row = []
        self.infos = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if len(attrs) == 3:
            # Rang
            if attrs[0][1].startswith("event-result-row"):
                # Reini la ligne
                self.row = []
                # Ajout du rang
                self.row.append(attrs[0][1].split("-")[-1])
                self.getvalue = True

    def handle_data(self, data):
        if self.getvalue:
            self.row.append(data)
            if len(self.row) > 5:  # On a récuperé les infos importantes
                self.getvalue = False
                # On ne prend en compte les données si on a un resultat incorrect
                if 'Notes:' not in self.row:
                    # Gender, Event, Location, Année, Rang, Nom, Pays, Resultat
                    self.save_row()

    def save_row(self):
        final_row = self.infos.copy()
        final_row.append(self.row[0])  # Rank
        final_row.append(self.row[3])  # Name
        final_row.append(self.row[2])  # Country
        if self.resultAsTime:
            result = self.row[5]
            # Format correct : 1:01:01.01
            if not re.match('(\d+):(\d+):(\d+\.\d+)$', result):
                # print("before",result)
                # format 1h01:01
                if re.match('(\d+)h(\d+):(\d+)', result):
                    result = re.sub("(\d+)h(\d+):(\d+)", "\\1:\\2:\\3", result)
                # format 1:01.01
                elif re.match('(\d+):(\d+)', result):
                    result = re.sub("(\d+):(\d+)", "0:\\1:\\2", result)
                # format 1.01
                elif re.match('(\d+\.\d+)', result):
                    result = re.sub("(\d+\.\d+)", "0:00:\\1", result)
                else:
                    return
                # format (pas de texte après le temps)
                if not re.match('(\d+:\d+:\d+\.?\d*)$', result):
                    result = re.sub("(\d+:\d+:\d+\.?\d*)(.*)", "\\1", result)
                # FORMATTAGE (1:1:1.10 -> 1:01:1.10)
                splitr = result.split(":")
                result = "{}:{:02d}:{}".format(splitr[0], int(splitr[1]), splitr[2])
                final_row.append(result)
        final_row.append(self.row[5])
        self.data.append(final_row)

    def scan(self, data, game, sport):
        sportSplitted = sport.split("-")
        self.infos = []
        self.infos.append("W" if sportSplitted[-1] == "women" else "M")  # Gender
        self.infos.append(" ".join(sportSplitted[0:-1]))  # Sport
        gameSplitted = game.split("-")
        self.infos.append(" ".join(gameSplitted[0:-1]))  # Location
        self.infos.append(gameSplitted[-1])  # Year
        self.feed(data)


class Sports:
    def __init__(self, category, sports, outputFile, time=False):
        self.category = category
        self.sports = sports
        self.outputFile = outputFile
        self.time = time
        # ajout season pour les jeux d'hiver


# Jeux
summerGames = ['rio-2016', 'london-2012', 'beijing-2008', 'athens-2004', 'sydney-2000', 'atlanta-1996',
               'barcelona-1992', 'seoul-1988', 'los-angeles-1984', 'moscow-1980', 'montreal-1976', 'munich-1972',
               'mexico-city-1968', 'tokyo-1964', 'rome-1960', 'melbourne-1956', 'helsinki-1952', 'london-1948',
               'berlin-1936', 'los-angeles-1932', 'amsterdam-1928', 'paris-1924', 'antwerp-1920',
               'stockholm-1912', 'london-1908', 'st-louis-1904', 'paris-1900', 'athens-1896']

winterGames = ['pyeongchang-2018', 'sochi-2014', 'vancouver-2010', 'torino-2006', 'salt-lake-city-2002', 'nagamo-1998',
               'lillehammer-1994', 'albertville-1994', 'calgary-1988', 'sarajevo-1984', 'lake-placid-1980',
               'innsbruck-1976', 'sapporo-1972', 'squaw-valley-1960', 'cortina-d-ampezzo-1956', 'oslo-1952',
               'st-moritz-1948', 'garmisch-partenkirchen-1936', 'lake-placid-1932', 'st-moritz-1928', 'chamonix-1924']


sportsRunning = ['100m-men', '100m-women', '200m-men', '200m-women', '400m-men', '400m-women', '800m-men', '800m-women',
                 '110m-hurdles-men', '100m-hurdles-women', '400m-hurdles-men', '400m-hurdles-women', '1500m-men',
                 '1500m-women', '5000m-men', '5000m-women', '10000m-men', '10000m-women', 'marathon-men',
                 'marathon-women']

sportsAthletics = ['discus-throw-men', 'discus-throw-women', 'hammer-throw-men', 'hammer-throw-women', 'high-jump-men',
                   'high-jump-women', 'javelin-throw-men', 'javelin-throw-women', 'long-jump-men', 'long-jump-women',
                   'pole-vault-men', 'pole-vault-women', 'shot-put-men', 'shot-put-women', 'triple-jump-men',
                   'triple-jump-women']

sportsSwimming = ['100m-backstroke-men', '100m-backstroke-women', '100m-breaststroke-men', '100m-breaststroke-women',
                  '100m-butterfly-men', '100m-butterfly-women', '100m-freestyle-men', '100m-freestyle-women',
                  '1500m-freestyle-men', '200m-backstroke-men', '200m-backstroke-women', '200m-breaststroke-men',
                  '200m-breaststroke-women', '200m-butterfly-men', '200m-butterfly-women', '200m-freestyle-men',
                  '200m-freestyle-women', '200m-individual-medley-men', '200m-individual-medley-women',
                  '400m-freestyle-men', '400m-freestyle-women', '50m-freestyle-men', '50m-freestyle-women']

fields = ["gender", "sport", "location", "year", "rank", "name", "country", "results"]

running = Sports('athletics', sportsRunning, 'running_results.csv', time=True)
athletics = Sports('athletics', sportsAthletics, 'athletics_results.csv')
swimming = Sports('swimming', sportsSwimming, 'swimming_results.csv', time=True)

# Changer pour selectionner :
sportsSelected = swimming

parser = MyHTMLParser(sportsSelected.time)

for game in winterGames:
    for sport in sportsSelected.sports:
        try:
            url = 'https://olympics.com/en/olympic-games/' + game + '/results/' + sportsSelected.category + '/' + sport
            u = urllib.request.urlopen(url)
            data = u.read().decode('utf8')
            parser.scan(data, game, sport)
        except HTTPError:
            print(game, sport, "introuvable")

print(parser.data)

with open(sportsSelected.outputFile, 'w', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(parser.data)
