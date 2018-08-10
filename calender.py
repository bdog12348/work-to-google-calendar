from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from twilio.rest import Client
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/calendar' #Scope for google calendar api

workSite =  #Site to login to see work schedule
userName =  #Username to login to site
password =  #Pass to login to site

inputUserID = #HTML ID for element to input username
inputPassID = #HTML ID for element to input password
submitID = #HTML ID for submit button

calendarID = #Calendar id from google calendars

timeZone = #Time zone info for google calendar
timeZoneOffset =  #Time zone offset for google calendar

def main():   
    store = file.Storage('token.json') #File generated after google authentication
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES) #Credentials from google calendar api
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    events = service.events().list(calendarId=calendarID).execute()

    driver = webdriver.Firefox() #Designate which browser for selenium to open
    driver.get(workSite)
    driver.find_element_by_id(inputUserID).send_keys(userName)
    driver.find_element_by_id(inputPassID).send_keys(password)
    driver.find_element_by_id(submitID).click()

    locales = driver.find_elements_by_xpath("//span[@class='hours']") #Xpath to html element that has the hours

    for i in range(len(locales)):
        time = locales[i].text
        other = locales[i].find_elements_by_xpath("..")
        other = other[0].find_elements_by_xpath(".//div[1]") #Xpath to get the date for work

        if len(other) > 0:
            date = other[0].text

            #get only first time slot
            time = time.split('-')
            endTime = time[1]
            endTime = endTime[1:]
            time = time[0]
            time = time[:-1]

            #parse times
            if time[-1:] == 'a':
                time = time[:-1]
                mini = time.split(':')[1]
                if int(mini) < 30:
                    leftOver = 30 - int(mini)
                    mini = 60 - leftOver
                    hrDif = -1
                else:
                    mini = int(mini) - 30
                hr = time.split(':')[0]
                hr = int(hr) + hrDif
                hr = str(hr)
                if int(hr) < 10:
                    hr = '0' + hr
            elif time[-1:] == 'p':
                time = time[:-1]
                mini = time.split(':')[1]
                mini = int(mini) - 30
                if int(mini) < 0:
                    mini = abs(mini)
                    hrDif = -1
                hr = time.split(':')[0]
                hr = int(hr) + hrDif
                hr = int(hr) + 12

            if endTime.find('a') > 0:
                endTime = endTime[:endTime.find('a')]
                endMini = endTime.split(':')[1]
                endHr = endTime.split(':')[0]
                endHr = str(endHr)
                if int(endHr) < 10:
                    endHr = '0' + endHr
            elif endTime.find('p') > 0:
                endTime = endTime[:endTime.find('p')]
                endMini = endTime.split(':')[1]
                endHr = endTime.split(':')[0]
                endHr = int(endHr) + 12

            hr = str(hr)
            mini = str(mini)
            endHr = str(endHr)
            endMini = str(endMini)

            #parse dates
            month = str(date.split('/')[0])
            day = str(date.split('/')[1])

            event = {
                'summary' : 'Work',
                'start' : {
                    'dateTime' : '2018-' + month + '-' + day + 'T' + hr + ':' + mini + ':00' + timeZoneOffset,
                    'timeZone': timeZone,
                },
                'end': {
                    'dateTime': '2018-' + month + '-' + day + 'T' + endHr + ':' + endMini + ':00' + timeZoneOffset,
                    'timeZone': timeZone,
                }
            }

            #Ensure that events don't get duplicated
            upload = True
            for prevEvent in events['items']:
                if event['start'] == prevEvent['start']:
                    upload = False
            
            #Upload events to calendar
            if upload:
                event = service.events().insert(calendarId = calendarID, body=event).execute()

    
    driver.close()

if __name__ == '__main__':
    main()