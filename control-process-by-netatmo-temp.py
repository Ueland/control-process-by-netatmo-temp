#!/usr/bin/python3
# encoding=utf-8

#####
# APP CONFIGURATION
####
minTemp=24.0 # Min temperature to start process if not running
maxTemp=27.2 # Max temperature where process is killed if running

programToWatch="something.sh" # Program to run based on temperature

# To get clientID and clientSecret, log in to https://dev.netatmo.com/myaccount/ and create an app, you will
# then find Client id and Client secret there.
clientID="************************"
clientSecret="*******************************"

username="YOUR NETATMO EMAIL"
password="YOUR NETATMO PASSWORD"

deviceID="" # You can leave this empty if you dont know, then run the program. It will then list all available device IDs

####
# END CONFIGURATION
####


scope="read_station"

import requests, sys, subprocess

try:
    # Get access token to work further with
        payload = {
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id':clientID,
                'client_secret': clientSecret,
                'scope': scope}

        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        response.raise_for_status()
        accessToken=response.json()["access_token"]


        # Load all devices so we have data to work with, unfortunatly we cannot get a single device`s tempreature
        deviceListResponse = requests.post("https://api.netatmo.com/api/devicelist", {'access_token':accessToken})
        deviceListResponse.raise_for_status()
        modules = deviceListResponse.json()['body']['modules']

        # List all available devices if we have not specified a deviceID yet
        if deviceID is "":
            print("No deviceID specified: Listing all available devices:\n\n")

            print("\tDEVICE ID\t\tDEVICE NAME\tTEMPERATURE")
            for module in modules:
                if 'Temperature' in module['data_type']:
                    print("\t", module['_id'], "\t", module['module_name'], "\t", module['dashboard_data']['Temperature'])
            print("__________________")
            sys.exit(2)

        # Get current temperature
        activeModule = ""
        for module in modules:
            if module['_id'] == deviceID:
                activeModule = module
                break

        if activeModule is "":
            print("Could not find a module with ID", deviceID, " misspelled or missing?")
            sys.exit(1)

        moduleTemp = module['dashboard_data']['Temperature']

        # Are we running?

        running = True
        try:
            subprocess.check_output(['pgrep', '-f', programToWatch])
        except:
            running = False

        # If we should run AND is not running, start
        if not running and moduleTemp <= minTemp:
            subprocess.Popen(programToWatch, stdout=subprocess.PIPE)
            sys.exit(0)

        # If we should NOT run and is running, stop
        if running and moduleTemp >= maxTemp:
            subprocess.run(['pkill', '-f', programToWatch])
            sys.exit(0)

except requests.exceptions.HTTPError as error:
    print(error.response.status_code, error.response.text)
