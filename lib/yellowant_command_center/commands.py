"""Code which actually takes care of application API calls or other business logic"""


from yellowant.messageformat import MessageClass , MessageAttachmentsClass, AttachmentFieldsClass
from ..yellowant_message_builder.messages import items_message, item_message
import requests
import logging
import json
from urllib.parse import urljoin
from ..yellowant_command_center import command_center
from ..yellowant_api.models import BOX_Credentials,UserIntegration
from ..yellowant_api import views
from django.conf import settings



#--------------------------------------------------------------BOX BEGINS-----------------------------------------------------------------------


oauth2URL = 'https://app.box.com/api/oauth2/token'
#refreshToken='aBYdADPlBmqvedygndL7woniOVZMJ0cGpFlfnMElitj9c1UyrGkHm6bt5o4DVUPI'
clientId='4qerinz9kgy7adw653wb90co0vg1drt8'
clientSecret='z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62'


#---------------------------------------------------------------DEFAULT VARIABLES OF SERVER---------------------------------------------

from boxsdk.network.default_network import DefaultNetwork
from pprint import pformat
from io import StringIO


# Import two classes from the boxsdk module - Client and OAuth2
from boxsdk import Client, OAuth2

# Define client ID, client secret, and developer token.
CLIENT_ID = None
CLIENT_SECRET = None
ACCESS_TOKEN = None

# Read app info from text file



class LoggingNetwork(DefaultNetwork):
    def request(self, method, url, access_token, **kwargs):
        """ Base class override. Pretty-prints outgoing requests and incoming responses. """
        #print('\x1b[36m{} {} {}\x1b[0m'.format(method, url, pformat(kwargs)))
        response = super(LoggingNetwork, self).request(
            method, url, access_token, **kwargs
        )
        # if response.ok:
        #     #print('\x1b[32m{}\x1b[0m'.format(response.content))
        # else:
        #     print('\x1b[31m{}\n{}\n{}\x1b[0m'.format(
        #         response.status_code,
        #         response.headers,
        #         pformat(response.content),
        #     ))
        return response


#oauth2 = OAuth2(CLIENT_ID[:-1], CLIENT_SECRET[:-1], access_token=ACCESS_TOKEN[:-1])

# client = Client(oauth2, LoggingNetwork())
# my = client.user(user_id='me').get()
# print(my['login'])





#--------------------------------------------------------------------------LIST ALL FILES & FOLDERS---------------------------------------------------------------

def list_all(args,user_integration):
    #print("LIST")
    bxc=BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN=bxc.BOX_ACCESS_TOKEN
    #print(ACCESS_TOKEN)
    REFRESH_TOKEN=bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN+" refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    #print("logged")
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN, 'client_id': clientId,
                                    'client_secret': clientSecret})
    #print("GOT TOKENS")
    # If the above gives a 4XX or 5XX error
    #getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    #print("GOT NEW TOKEN")
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    # print("New accessToken " + accessToken)
    # print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN=refreshToken
    bxc.BOX_ACCESS_TOKEN=accessToken
    bxc.save()



    # Get the new access token, valid for 60 minutes


    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=accessToken)
    #print("listing...")
    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    #print("List of all files and folders\n")
    attachment = MessageAttachmentsClass()
    m=MessageClass()
    x=''
    for item in items:
        field=AttachmentFieldsClass()
        field.title=item['name']
        field.value=item['id']
        #print("Name: "+item['name']+" ID: "+item['id'])
        x=x+"Name: "+item['name']+" ID: "+item['id']+"\n"
        attachment.attach_field(field)
    m.attach(attachment)
    return m
    #print("\n\n")

#--------------------------------------------------------------------------USER DETAILS----------------------------------------------------------------------------

def user_details(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    #print("New accessToken " + accessToken)
    #print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()

    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=accessToken)
    attachment = MessageAttachmentsClass()

    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    # print("List of all files and folders\n")
    m = MessageClass()
    #print("The users are:\n")

    my = client.user(user_id='me').get()
    field=AttachmentFieldsClass()
    field.title="LOGIN ID"
    field.value=my['login']
    attachment.attach_field(field)
    m.attach(attachment)
    #print(my)
    return m

#------------------------------------------------------------------------CREATE SUB FOLDER---------------------------------------------------------------------------

def create_folder(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    #print("New accessToken " + accessToken)
    #print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()


    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)

    name=args['Folder-Name']
    client = Client(oauth2, LoggingNetwork())
    #items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    #print("List of all files and folders")
    #print("created "+name)
    m = MessageClass()
    client.folder(folder_id='0').create_subfolder(name)
    field=AttachmentFieldsClass()
    field.title="Successfully created the folder "+name
    attachment=MessageAttachmentsClass()
    attachment.attach_field(field)
    m.attach(attachment)
    return m
#------------------------------------------------------------------------RENAME A FILE-----------------------------------------------------------------------------
def rename(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    #print("New accessToken " + accessToken)
    #print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()


    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
    old_name = args['Old-Name']
    new_name = args['New-Name']
    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    #print("searching for item...")
    flag=0
    for item in items:
        # print(item['name'])
        if item['name']==old_name:
            #print("Name: " + item['name'] + " ID: " + item['id'])
            file_id=item['id']
            flag=1
            break


    #print("File name altered")
    field=AttachmentFieldsClass()
    attachment=MessageAttachmentsClass()
    if flag==1:
        field.title=old_name+" has been renamed to "+new_name
        attachment.attach_field(field)
        client.file(file_id=int(file_id)).rename(new_name)
    else:
        field.title=old_name + " does not exist."
        attachment.attach_field(field)

    m=MessageClass()
    m.attach(attachment)
    return m

#------------------------------------------------------------------------MOVE A FILE---------------------------------------------------------------------------------
def move_file(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    # print("New accessToken " + accessToken)
    # print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()


    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
    file_name = args['File-Name']
    folder_name = args['Folder-Name']
    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
   # print("searching for item...")
    flag=0
    for item in items:
        # print(item['name'])
        if item['name'] == file_name:
            print("Name: " + item['name'] + " ID: " + item['id'])
            file_id = item['id']
            flag=flag+1
        if item['name']==folder_name:
            print("Name: " + item['name'] + " ID: " + item['id'])
            folder_id=item['id']
            flag=flag+1


    field = AttachmentFieldsClass()
    attachment = MessageAttachmentsClass()
    if flag == 2:
        field.title = file_name + " has been moved to the folder " + folder_name
        attachment.attach_field(field)
        client.file(file_id=file_id).move(client.folder(folder_id=folder_id))
    else:
        field.title = "Either "+file_name +" or "+folder_name+ " does not exist."
        attachment.attach_field(field)

    m = MessageClass()
    m.attach(attachment)


    #print("Move successful")
    return m
#-----------------------------------------------------------------------GET CONTENT OF A FILE-----------------------------------------------------------------------
def file_content(args,user_integration):
    #print("The file has\n")
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    #print("New accessToken " + accessToken)
    #print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()

    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
    file_name = args['File-Name']

    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    flag=0
    for item in items:
        # print(item['name'])
        if item['name'] == file_name:
            print("Name: " + item['name'] + " ID: " + item['id'])
            file_id = item['id']
            flag=1

    field = AttachmentFieldsClass()
    attachment = MessageAttachmentsClass()
    if flag == 1:
        s = client.file(file_id=file_id).content()
        response = json.loads(s)
        response = response['atext']['text']
        field.title = "The file contains"
        field.value=response
        attachment.attach_field(field)
    else:
        field.title = file_name +" does not exist."
        attachment.attach_field(field)

    m = MessageClass()
    m.attach(attachment)



    response=json.loads(s)

    response=response['atext']['text']


    return m
#-------------------------------------------------------------------------SEARCH FOR A SPECIFIC FILE-----------------------------------------------------------------

def search_item(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    #print("New accessToken " + accessToken)
    #print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()

    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
    item_name = args['Item-Name']

    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    x=''
    #print("searching for item...")
    count=0
    attachment=MessageAttachmentsClass()
    for item in items:
        #print(item['name'])
        if item['name'].lower().find(item_name.lower()) ==-1:
            pass
        else:
            #print("Name: "+item['name']+" ID: "+item['id'])
            field=AttachmentFieldsClass()
            field.title=item['name']
            field.value=item['id']
            x=x+"Name: "+item['name']+" ID: "+item['id']+"\n"
            count=count+1
            attachment.attach_field(field)
    m = MessageClass()
    if count==0:
        field=AttachmentFieldsClass()
        field.title="No files found that match "+item_name
        attachment.attach_field(field)
        m.attach(attachment)
        return m

    m.attach(attachment)
    return m

#-----------------------------------------------------------------------DOWNLOAD FILE--------------------------------------------------

def download_file(args,user_integration):
    bxc = BOX_Credentials.objects.get(user_integration_id=user_integration)
    ACCESS_TOKEN = bxc.BOX_ACCESS_TOKEN
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN

    #print(ACCESS_TOKEN)
    REFRESH_TOKEN = bxc.BOX_REFRESH_TOKEN
    #print(REFRESH_TOKEN + " refreshtoken")

    # Log the token we're using & starting call
    logging.info('Using Refresh Token: %s' % REFRESH_TOKEN)
    # Get new access & refresh tokens
    getTokens = requests.post(oauth2URL,
                              data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN,
                                    'client_id': clientId,
                                    'client_secret': clientSecret})
    # If the above gives a 4XX or 5XX error
    # getTokens.raise_for_status()
    # Get the JSON from the above
    newTokens = getTokens.json()
    # Get the new access token, valid for 60 minutes
    accessToken = newTokens['access_token']
    refreshToken = newTokens['refresh_token']
    # print("New accessToken " + accessToken)
    # print("New refreshToken " + refreshToken)
    bxc.BOX_REFRESH_TOKEN = refreshToken
    bxc.BOX_ACCESS_TOKEN = accessToken
    bxc.save()

    CLIENT_ID = settings.CLIENT_ID
    CLIENT_SECRET = settings.CLIENT_SECRET

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
    file_name = args['File-Name']

    client = Client(oauth2, LoggingNetwork())
    items = client.folder(folder_id='0').get_items(limit=1000, offset=0)
    flag=0
    for item in items:
        if item['name']==file_name:
            file_id=item['id']
            flag=1
            break
    field=AttachmentFieldsClass()
    if flag==1:
        field.title="Press the link below to download file"
        field.value='https://app.box.com/file/'+str(file_id)
    else:
        field.title="File not found"

    attachment=MessageAttachmentsClass()
    attachment.attach_field(field)

            #print(item['name']+" id-> "+item['id'])
    #print('https://app.box.com/file/'+file_id)
    #
    #
    #
    #
    #
    #
    #
    #
    # access_token = accessToken
    # headers = {'Authorization': 'Bearer ' + access_token}
    # url = 'https://api.box.com/2.0/webhooks'
    #
    # # Define webhook fields
    # data = {
    #     "target": {
    #         "id": file_id,
    #         "type": "file"
    #     },
    #     "address": 'https://00c6567b.ngrok.io/webhooks/',
    #     "triggers": ["FILE.DOWNLOADED"]
    # }
    #
    # # Make request to create new webhook
    # response = requests.post(url, data=json.dumps(data), headers=headers)
    # jsonres = response.json()
    #
    # print(jsonres)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    m=MessageClass()
    m.attach(attachment)
    return m

#------------------------------------------------------------------------UPLOAD FILE----------------------------------------------------
#WONT WORK
# def upload_file(name):
#     stream = StringIO()
#     stream.write('Box Python SDK test!')
#     stream.seek(0)
#     box_file = client.folder('0').upload_stream(stream, '')
#     print(box_file.name)



#download_file('DSC_0015.jpg')
#create_folder()
#rename('6024373299','Pic1.jpg')
#list_all()
#move_file('6151889631','50321142563')
#file_content('298279015217')

#search_item('DSC')


