import json
import logging
import os
import plistlib
import requests
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText

# Variables
oauth2URL = 'https://app.box.com/api/oauth2/token'
apiURL = 'https://api.box.com/2.0/'
authorizationCode = '9tqKkbKX8EQ6I68gUy14pqu8iDJYQPTA'
clientId = '4qerinz9kgy7adw653wb90co0vg1drt8'
clientSecret = 'z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62'
apiFolder = '/mnt/15afd8d4-23a1-4733-9204-2964d3811cd6/box/yellowant_BOX/lib/yellowant_command_center'
logFileFullPath = os.path.join(apiFolder, os.path.basename(sys.argv[0]) + '.log')
plistFileFullPath = os.path.join(apiFolder, 'Box-API.plist')
mailServer = ''
mailFrom = ''
mailTo = ''

# Get Script Name
scriptName =  os.path.basename(sys.argv[0])
# Configure Logging
logging.basicConfig(filename=logFileFullPath,level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',filemode='w')

# Send email
def sendEmail(statusMessage):
    # Open the logFile as email contents
    logFile = open(logFileFullPath, 'rb')
    # Create a text/plain message
    msg = MIMEText(logFile.read())
    logFile.close()
    # Email From, To & Subject
    msg['From'] = mailFrom
    msg['To'] = mailTo
    msg['Subject'] = scriptName + ": " + statusMessage
    # Send the email
    s = smtplib.SMTP(mailServer)
    s.sendmail(mailFrom, mailTo, msg.as_string())
    s.quit()
    # Exit script
    sys.exit(0)

# Generate OAuth2 tokens
def generateTokens():
    # Read this scripts plist
    # try:
    #     # Read this scripts plist
    #     print("TRYING")
    #     tokenPlist = plistlib.readPlist(plistFileFullPath)
    #     # Get the Refresh token from the plist
    #     refreshToken = tokenPlist["Refresh Token"]
    #
    # # If we can't find the plist
    # except:
    #     # Try & generate new tokens
    try:
        # API call to generate tokens
        getTokens = requests.post(oauth2URL, data={'grant_type' : 'authorization_code','code' : authorizationCode, 'client_id' : clientId, 'client_secret' : clientSecret})
        # If the above gives a 4XX or 5XX error
        print(getTokens)
        #getTokens.raise_for_status()
        # Get the JSON from the above
        newTokens = getTokens.json()
        # Get the new access token, valid for 60 minutes
        accessToken = newTokens['access_token']
        print(accessToken)
        # Log the access token we're using
        logging.info('Generated Access Token: %s' % accessToken)
        # Get the refresh token, valid for 60 days
        refreshToken = newTokens['refresh_token']
        print(refreshToken)
        # Log the new refresh token we've generated
        logging.info('Generated Refresh Token: %s' % refreshToken)
        # Update plist with new refresh token & time generated, refresh token used for subsequent runs
        plistlib.writePlist({'Refresh Token':refreshToken,'Time Generated': datetime.now().isoformat(),}, plistFileFullPath)
        # Update tokenPlist variable
        tokenPlist = plistlib.readPlist(plistFileFullPath)
    # If we cannot generate the tokens
    except requests.exceptions.RequestException as e:
        # Status message to use as subject for sendMail funtion
        statusMessage = 'Cannot generate tokens %s' % e
        # Advise that no devices are to be deleted
        logging.error('-------- ' + statusMessage + ' --------')
        # Email & exit
        sendEmail(statusMessage)
    # If we cannot create the plist
    except:
        # Status message to use as subject for sendMail funtion
        statusMessage = 'Cannot create plist'
        # Advise that no devices are to be deleted
        logging.error('-------- ' + statusMessage + ' --------')
        # Email & exit
        sendEmail(statusMessage)

    # Try to make the API call
    try:
        # Log the token we're using & starting call
        logging.info('Using Refresh Token: %s' % refreshToken)
        # Get new access & refresh tokens
        getTokens = requests.post(oauth2URL, data={'grant_type' : 'refresh_token','refresh_token' : refreshToken, 'client_id' : clientId, 'client_secret' : clientSecret})
        # If the above gives a 4XX or 5XX error
        getTokens.raise_for_status()
        # Get the JSON from the above
        newTokens = getTokens.json()
        # Get the new access token, valid for 60 minutes
        accessToken = newTokens['access_token']
        print("New accessToken "+accessToken)
        # Log the access token we're using
        logging.info('Generated Access Token: %s' % accessToken)
        # Get the refresh token, valid for 60 days
        refreshToken = newTokens['refresh_token']
        # Log the new refresh token we've generated
        logging.info('Generated Refresh Token: %s' % refreshToken)
        # Update plist with new refresh token & time generated, refresh token used for subsequent runs
        plistlib.writePlist({'Refresh Token':refreshToken,'Time Generated': datetime.now().isoformat(),}, plistFileFullPath)
        # Email & exit
        #sendEmail('Successfully Generated Tokens')
    # If the API call fails, report error as e
    except requests.exceptions.RequestException as e:
        # Status message to use as subject for sendMail funtion
        statusMessage = 'Get request failed with %s' % e
        # Advise that no devices are to be deleted
        logging.error('-------- ' + statusMessage + ' --------')
        # Email & exit
        sendEmail(statusMessage)

# Run functions in this order
if __name__ == '__main__':
    # Generate the API Tokens
    generateTokens()