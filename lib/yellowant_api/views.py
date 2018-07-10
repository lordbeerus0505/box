from datetime import datetime
import json, uuid
import os
import plistlib
import sys

import requests
import logging
from boxsdk import OAuth2
from boxsdk import Client
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.models import User
from django.conf import settings

from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from yellowant import YellowAnt
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass

from .models import YellowAntRedirectState, UserIntegration, BOX_Credentials
from ..yellowant_command_center.command_center import CommandCenter

integ_id=0
access_token='hello'
refresh_token=''
access=''
refres=''
ut=0
def generateTokens(clientId,clientSecret,oauth2URL,apiUrl,authorizationCode):
    print("INSIDE GENERATE TOKENS")
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
    apiFolder = '/mnt/15afd8d4-23a1-4733-9204-2964d3811cd6/box/yellowant_BOX/lib/yellowant_command_center'
    logFileFullPath = os.path.join(apiFolder, os.path.basename(sys.argv[0]) + '.log')
    plistFileFullPath = os.path.join(apiFolder, 'Box-API.plist')
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
        #sendEmail(statusMessage)
    # If we cannot create the plist
    except:
        # Status message to use as subject for sendMail funtion
        statusMessage = 'Cannot create plist'
        # Advise that no devices are to be deleted
        logging.error('-------- ' + statusMessage + ' --------')
        # Email & exit
        #sendEmail(statusMessage)

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
        print("New refreshToken "+refreshToken)

        bxc=BOX_Credentials.objects.get(user_integration_id=ut)
        bxc.BOX_ACCESS_TOKEN=accessToken
        bxc.BOX_REFRESH_TOKEN=refreshToken
        bxc.BOX_UPDATE_LOGIN_FLAG=True
        bxc.save()
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
        #sendEmail(statusMessage)


def store_tokens(access_token, refresh_token):
    global access, refresh
    access=access_token
    refresh=refresh_token


def box_return(request):
    print("Inside box_return")
    code=request.GET.get("code")
    state=request.GET.get("state")
    print(code)
    clientId = '4qerinz9kgy7adw653wb90co0vg1drt8'
    clientSecret = 'z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62'
    oauth2URL = 'https://app.box.com/api/oauth2/token'
    apiURL = 'https://api.box.com/2.0/'
    authorizationCode = code
    generateTokens(clientId,clientSecret,oauth2URL,apiURL,authorizationCode)
    return HttpResponseRedirect("/")

def request_yellowant_oauth_code(request):
    """Initiate the creation of a new user integration on YA
    
    YA uses oauth2 as its authorization framework. This method requests for an oauth2 code from YA to start creating a 
    new user integration for this application on YA.
    """
    # get the user requesting to create a new YA integration 
    user = User.objects.get(id=request.user.id)
    print("Hello 1st\n\n")
    # generate a unique ID to identify the user when YA returns an oauth2 code
    state = str(uuid.uuid4())
    print("state in "+state)

    # save the relation between user and state so that we can identify the user when YA returns the oauth2 code
    data = YellowAntRedirectState.objects.create(user=user.id, state=state)
    print("Data" ,data)

    # Redirect the application user to the YA authentication page. Note that we are passing state, this app's client id,
    # oauth response type as code, and the url to return the oauth2 code at.
    return HttpResponseRedirect("{}?state={}&client_id={}&response_type=code&redirect_url={}".format(
        settings.YA_OAUTH_URL, state, settings.YA_CLIENT_ID, settings.YA_REDIRECT_URL))


def yellowant_oauth_redirect(request):
    global ut
    """Receive the oauth2 code from YA to generate a new user integration
    
    This method calls utilizes the YA Python SDK to create a new user integration on YA.
    This method only provides the code for creating a new user integration on YA. Beyond that, you might need to 
    authenticate the user on the actual application (whose APIs this application will be calling) and store a relation
    between these user auth details and the YA user integration.
    """
    # oauth2 code from YA, passed as GET params in the url
    print('inside yellowant_oauth_redirect')
    code = request.GET.get("code")
    print(code)

    print("Hello 2nd\n\n")

    # the unique string to identify the user for which we will create an integration
    state = request.GET.get("state")
    print("state is 2nd")
    print(state)
    # fetch user with the help of state
    yellowant_redirect_state = YellowAntRedirectState.objects.get(state=state)
    user = yellowant_redirect_state.user
    print("user is")
    print(user)

    # initialize the YA SDK client with your application credentials
    ya_client = YellowAnt(app_key=settings.YA_CLIENT_ID, app_secret=settings.YA_CLIENT_SECRET, access_token=None,
        redirect_uri=settings.YA_REDIRECT_URL)


    # get the access token for a user integration from YA against the code
    print ("here")
    access_token_dict = ya_client.get_access_token(code)
    print(str(access_token_dict)+" Accesstoken")
    print("Inside \n\n")
    access_token = access_token_dict["access_token"]

    # reinitialize the YA SDK client with the user integration access token
    ya_client = YellowAnt(access_token=access_token)

    # get YA user details
    ya_user = ya_client.get_user_profile()

    # create a new user integration for your application
    user_integration = ya_client.create_user_integration()

    # save the YA user integration details in your database
    ut=UserIntegration.objects.create(user=user, yellowant_user_id=ya_user["id"],
        yellowant_team_subdomain=ya_user["team"]["domain_name"],
        yellowant_integration_id=user_integration["user_application"],
        yellowant_integration_invoke_name=user_integration["user_invoke_name"],
        yellowant_integration_token=access_token)

    BOX_Credentials.objects.create(user_integration=ut, BOX_ACCESS_TOKEN="",BOX_REFRESH_TOKEN="", BOX_UPDATE_LOGIN_FLAG=False)
    
    # A new YA user integration has been created and the details have been successfully saved in your application's 
    # database. However, we have only created an integration on YA. As a developer, you need to begin an authentication 
    # process for the actual application, whose API this application is connecting to. Once, the authentication process 
    # for the actual application is completed with the user, you need to create a db entry which relates the YA user
    # integration, we just created, with the actual application authentication details of the user. This application
    # will then be able to identify the actual application accounts corresponding to each YA user integration.

    # return HttpResponseRedirect("to the actual application authentication URL")

    print(str(user_integration["user_application"])+"  integration ID")

    # agc=Agile_Credentials()
    # agc.user_integration=UserIntegration.objects.get(yellowant_integration_id=user_integration["user_application"])
    # agc.save()
    global integ_id
    integ_id= UserIntegration.objects.get(yellowant_integration_id=user_integration["user_application"])
    oauth = OAuth2(
        client_id='4qerinz9kgy7adw653wb90co0vg1drt8',
        client_secret='z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62',
        store_tokens=store_tokens(access_token, refresh_token),
    )
    auth_url, csrf_token = oauth.get_authorization_url('https://box123.herokuapp.com//return/')
    url=auth_url
    print(url)
    return HttpResponseRedirect(url)
    #reverse ('/')


@csrf_exempt
def yellowant_api(request):
    """Receive user commands from YA"""
    data = json.loads(request.POST.get("data"))

    # verify whether the request is genuinely from YA with the help of the verification token
    if data["verification_token"] != settings.YA_VERIFICATION_TOKEN:
        return HttpResponseNotAllowed("Insufficient permissions.")
    
    # check whether the request is a user command, or a webhook subscription notice from YA
    if data["event_type"] == "command":
        # request is a user command

        # retrieve the user integration id to identify the user
        yellowant_integration_id = data.get("application")

        # invoke name of the command being called by the user
        command_name = data.get("function_name")

        # any arguments that might be present as an input for the command
        args = data.get("args")

        # create a YA Message object with the help of the YA SDK
        message = CommandCenter(yellowant_integration_id, command_name, args).parse()

        # return YA Message object back to YA
        return HttpResponse(message)
    elif data["event_type"] == "webhook_subscription":
        # request is a webhook subscription notice
        pass



#------------------------------------------------------------------------------------------------------------------------



def api_key(request):
    """An object is created in the database using the request."""
    print("Inside api_key")
    data = json.loads(request.body)



    try:
        #print(1)
        abc=BOX_Credentials()
        x=data['user_integration']
        print(x)
        aby = BOX_Credentials.objects.get(user_integration_id=int(data["user_integration"]))
        print(2)
        #aby.BOX_CLIENT_ID = data['BOX_CLIENT_ID']
        #print(aby.BOX_CLIENT_ID)
        #aby.BOX_CLIENT_SECRET = data['BOX_CLIENT_SECRET']
        #print(4)
        aby.BOX_ACCESS_TOKEN = data['BOX_ACCESS_TOKEN']
        print(555)
        # aby.AZURE_client_secret = data['AZURE_client_secret']
        aby.BOX_REFRESH_TOKEN=data['BOX_REFRESH_TOKEN']
        aby.BOX_UPDATE_LOGIN_FLAG = True

        print("Hello"+aby.BOX_ACCESS_TOKEN + "  " + aby.BOX_REFRESH_TOKEN+ "  ")
        aby.save()
    except:
        return HttpResponse("Invalid credentials. Please try again")


    # else:
    #     #aby = Agile_Credentials.objects.get(user_integration_id=int(data["user_integration_id"]))
    #     aby=Agile_Credentials()
    #     aby.AGILE_API_KEY = data['AGILE_API_KEY']
    #     aby.AGILE_EMAIL_ID = data['AGILE_EMAIL_ID']
    #     aby.AGILE_DOMAIN_NAME = data['AGILE_DOMAIN_NAME']
    #     #aby.AZURE_client_secret = data['AZURE_client_secret']
    #     aby.AGILE_UPDATE_LOGIN_FLAG = True
    #     print(aby.AGILE_API_KEY + "  " + aby.AGILE_DOMAIN_NAME + "  " + aby.AGILE_EMAIL_ID)
    #     aby.save()


    return HttpResponse("Success", status=200)


# def get_credentials(tenant, client, subs, secret):
#     """Function to get credentials of the AZURE account"""
#     subscription_id = subs
#     credentials = ServicePrincipalCredentials(
#         client_id=client,
#         secret=secret,
#         tenant=tenant
#     )
#     return credentials, subscription_id


@csrf_exempt
def webhooks(request):
    #print(request.post.data)
    # print(type(request))
    print((request.body))
    print("INSIDE WEBHOOKS")
    print("REq== "+str(request))

    # file_id = 'ID OF FILE TO ADD WEBHOOK TO';
    # notification_url = 'https://www.YOURSITE.com/NOTIFICATION';
    # oauth = OAuth2(
    #         client_id='4qerinz9kgy7adw653wb90co0vg1drt8',
    #         client_secret='z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62',
    #         store_tokens=store_tokens(access_token,refresh_token),
    #     )

    # Define https request info
    access_token = 'gcfGTUCtbKzXItgnyqG0ClR4JERVTkR3'
    headers = {'Authorization': 'Bearer ' + access_token}
    url = 'https://api.box.com/2.0/webhooks'
    print("crossed")
    # Define webhook fields
    data = {
        "target": {
            "id": '6024373299',
            "type": "file"
        },
        "address": 'https://00c6567b.ngrok.io/webhooks/',
        "triggers": ["FILE.RENAMED"]
    }

    # Make request to create new webhook
    print(json.dumps(data)," Data")
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response,"  RESPONSE")
    # jsonres = response.json()
    # print(jsonres)
    # try:
    #     print("Body is")
    #     body=json.loads(json.dumps((request.body.decode("utf-8"))))
    #
    #
    #
    #     print(body)
    # # print(json.loads(body))
    #     body=json.loads(body)
    #     print("TRY")
    # except:
    #     return HttpResponse("Failed", status=404)
    #     print("EXCEPT")
    #
    # # print(body['sys_id'])
    # print("getting user")
    # User = UserIntegration.objects.get(webhook_id=ut)
    # service_application = str(User.yellowant_integration_id)
    # access_token = User.yellowant_integration_token
    #
    #
    #
    # #######    STARTING WEB HOOK PART
    # webhook_message = MessageClass()
    # webhook_message.message_text = "Incident" + " " + body['state']
    # attachment = MessageAttachmentsClass()
    # field1 = AttachmentFieldsClass()
    # field1.title = "Incident Name"
    # field1.value = body['number']
    # attachment.attach_field(field1)
    # webhook_message.attach(attachment)
    #
    # attachment = MessageAttachmentsClass()
    # field1 = AttachmentFieldsClass()
    # field1.title = "Incident Description"
    # field1.value = body['description']
    # attachment.attach_field(field1)
    # webhook_message.attach(attachment)
    #
    #
    #
    # # Creating yellowant object
    # yellowant_user_integration_object = YellowAnt(access_token=access_token)
    #
    # # Sending webhook message to user
    # send_message = yellowant_user_integration_object.create_webhook_message(
    #     requester_application=User.yellowant_integration_id,
    #     webhook_name="webhook", **webhook_message.get_dict())
    return HttpResponse("OK", status=200)