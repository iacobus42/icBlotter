import urllib
from bs4 import BeautifulSoup
import sqlite3 as lite
import json
import time
import datetime

database = "/path/to/data/base.db"
apiKey = "&key=your-google-api-key"

# this program should not require any changes

baseUrl = "http://www.iowa-city.org/icgov/apps/police/activityLog.asp?date="

def genericClean(cell):
  contents = cell.getText().replace(u'\xa0', '').encode('utf-8').strip()
  return contents

def addressClean(cell, key):
  gBase = "https://maps.googleapis.com/maps/api/geocode/json?"
  content = genericClean(cell)
  address = urllib.quote_plus(content, ",")
  address = address.replace("'", "")
  qURL = gBase + "address=" + address + "+iowa+city,+ia" + key
  results = json.load(urllib.urlopen(qURL))
  try:
    lng = results['results'][0]['geometry']['location']['lng']
    lat = results['results'][0]['geometry']['location']['lat']
  except:
    lng = "NULL"
    lat = "NULL"
  return [content, lat, lng]
  
def timeClean(cell):
  contents = genericClean(cell)
  contents = contents.split()
  if contents[1] == "pm":
    contents = contents[0].split(":")
    hour = str(int(contents[0]) + 12)
    minute = int(contents[1])
  else:
    contents = contents[0].split(":")
    hour = int(contents[0])
    if hour == 12:
      hour = 0
    minute = int(contents[1])
  return [hour, minute]

def cleanNote(cell, m, d, y, dispatchNumber):
  contents = genericClean(cell)
  if contents == '\xc2\x95':
    note = True
    url = "http://www.iowa-city.org/icgov/apps/police/activityLog.asp?dis="
    url = url + str(dispatchNumber) + "&date=" + str(m) + str(d) + str(y)
    html = urllib.urlopen(url)
    soup = BeautifulSoup(html)
    detailTable = soup.find("table", attrs = {"width":"600"})
    rows = detailTable.find_all("tr")
    note = genericClean(rows[7].find("td"))
  else:
    note = "NULL"
  return note

def getDailyLog(month, day, year, db = database):
  con = lite.connect(db)
  cur = con.cursor()
  month = str(month)
  day = str(day)
  if len(month) == 1:
    month = "0" + month
  if len(day) == 1:
    day = "0" + day
  url = baseUrl + month + day + str(year)
  html = urllib.urlopen(url)
  soup = BeautifulSoup(html)
  tattrs = {'cellpadding':'2','cellspacing':'1'}
  eventsTable = soup.find("table", attrs = tattrs)
  events = eventsTable.find_all("tr")
  nEvents = len(events)
  print url
  for i in range(1, nEvents):
    t1 = time.time()
    event = events[i]
    cells = event.find_all("td")
    # dispatch number
    dispatchNumber = genericClean(cells[0])
    # inc number
    incNumber = genericClean(cells[1])
    if incNumber == "":
      incNumber = "NULL"
    # activity
    activity = genericClean(cells[2])
    # disposition  
    disposition = genericClean(cells[3])
    # location
    location = addressClean(cells[4], apiKey)
    # apt
    apt = genericClean(cells[5])
    if apt == "":
      apt = "NULL"
    # time
    timeStamp = timeClean(cells[6])
    # note
    note = cleanNote(cells[7], month, day, year, dispatchNumber)
    eventID = str(month) + str(day) + str(year) + str(dispatchNumber)
    cur.execute("INSERT INTO events VALUES(" + 
    str(eventID) + "," +
    str(dispatchNumber) + "," + str(incNumber) + "," +
    str(int(month)) + "," + str(int(day)) + "," + str(int(year)) + "," +
    str(timeStamp[0]) + "," + str(timeStamp[1]) + "," +
    "'" + str(location[0]) + "'," + str(location[1]) + "," + 
    str(location[2]) + "," +
    "'" + str(apt) + "'," +
    "'" + activity + "','" + disposition + "','" + note + "')")
    d = time.time() - t1
    if d < 0.25:
      time.sleep(0.25 - d)
  con.commit()
  con.close()
  
yday = datetime.date.fromordinal(datetime.date.today().toordinal()-1)
getDailyLog(yday.month, yday.day, yday.year)
