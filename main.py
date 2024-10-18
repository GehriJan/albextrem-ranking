import sys
import getopt
from urllib.request import urlopen
import requests
import io
import PyPDF2
import re
from typing import Optional
def processOptions(opts):
    for opt, optarg in opts:
        if opt == "-h" or opt == "--help":
            sys.exit()

class Rider:
    def __init__(self, name: str, time: str, distance: int) -> None:
        self.name = name
        self.time = time
        self.distance = distance
    def __repr__(self) -> str:
        return f"Name: {self.name}\t\tDistance: {self.distance}km Time: {self.time}h"
    def getHours(self) -> float:
        times = re.findall("\d\d", self.time)
        hours = int(times[0])
        minutes = int(times[1])
        seconds = int(times[2])
        return hours + minutes/60 + seconds/3600
    def getVelocity(self):
        return self.distance/self.getHours()

def getPdfText(url: str) -> Optional[str]:
    response = requests.get(url)
    if response.status_code!=200:
        return None
    with io.BytesIO(response.content) as open_pdf_file:
        reader = PyPDF2.PdfReader(open_pdf_file)
        text: str = ""
        for page in reader.pages:
            text+=page.extract_text()
        return text
        
def getRider(id: int) -> Optional[Rider]:
        print(f"get rider with id: {id}")
        url = f"https://my1.raceresult.com/296384/certificates/{id}/Alle%20f%C3%BCr%20Internet%20ohne%20Hintergrund"
        text = getPdfText(url)
        if text==None:
            exceptions.append(id)
            return None
        lines = text.splitlines()
        
        name = lines[0].strip()
        if  len(re.findall("... km", lines[len(lines)-2]))==0 or\
            len(re.findall("\d\d:\d\d:\d\d", lines[len(lines)-1]))==0:
            exceptions.append(id)
            return None
        distanceLine = re.findall("... km", lines[len(lines)-2])[0]
        distance = int(distanceLine[:len(distanceLine)-3].strip())
        time = re.findall("\d\d:\d\d:\d\d", lines[len(lines)-1])[0].strip()
        return Rider(name, time, distance)

def getRiderIDs() -> list[int]:
        url = f"https://my1.raceresult.com/296384/RRPublish/data/pdf?name=Presenter%2FModerator%7CErgebnisliste%20ALLE%20Distanzen%20ohne%20Zeit&contest=0&lang=de"
        text = getPdfText(url)
        f = open("riders.txt", "w")
        f.write(text)
        f.close()

def read_numbers_from_file(filename):
    with open(filename, 'r') as file:
        numbers = [int(line.strip()) for line in file if line.strip().isdigit()]
    return numbers

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],
                                    "h",
                                    ["help"])
except getopt.GetoptError as err:
    print(sys.argv[0],":", err)
    sys.exit(1)

processOptions(opts)
riders: list[Rider] = []
ids = read_numbers_from_file("riders.txt")
exceptions = []
for id in ids:
    rider = getRider(id)
    if rider is not None:
        riders.append(rider)
    print(rider)
riders = sorted(riders, key=lambda rider: (-rider.distance, rider.getHours()))
output = "Nummer,Name,Distanz,Zeit,Geschwindigkeit\n"
riderCtr = {
    "90": 0,
    "170": 0,
    "220": 0,
    "270": 0,
    "310": 0
}
currentDistance = 0
formerDistance = 0
i = 0
for rider in riders:
    if formerDistance == rider.distance:
        i+=1
    else:
        i=1
    output+=f"{i},{rider.name};{rider.distance};{rider.time};{rider.getVelocity()}\n"
    riderCtr[str(rider.distance)]+=1
    formerDistance = rider.distance
output = output.replace(".",",")
with open("albextremOutput.csv", "w") as outputFile:
        outputFile.write(output)
        outputFile.close()
print(f"In List: {riderCtr['90']+riderCtr['170']+riderCtr['220']+riderCtr["270"]+riderCtr['310']}")
print(f"Not in list: {len(exceptions)}")