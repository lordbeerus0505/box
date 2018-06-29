from boxsdk import OAuth2
from boxsdk import Client
from django.http import HttpResponse,HttpResponseRedirect
import requests
import logging



access_token='hello'
refresh_token=''
access=''
refres=''

# def store_tokens(access_token, refresh_token):
#     access=access_token
#     refresh=refresh_token
#
# oauth = OAuth2(
#     client_id='4qerinz9kgy7adw653wb90co0vg1drt8',
#     client_secret='z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62',
#     store_tokens=store_tokens(access_token,refresh_token),
# )
# auth_url, csrf_token = oauth.get_authorization_url('https://0.0.0.0')
# print(auth_url+"   AuthURl")
# print(csrf_token+"    csrf token")
# print("Access TOken="+access_token)
#
# #assert 'box_csrf_token_uhZ0yOdXWjxaxnv3 ' == csrf_token
# auth='TOfmU5bqCY81HyHhMoiQZzElCu3QWied'
# access_token,refresh_token=oauth.authenticate(auth)
# response=requests.get(auth_url)
# r = requests.get(auth_url)
# print(r.url)
# #print(response.text)
# print("Access token "+access_token)
# print("Refresh TOken "+refresh_token)
#
# client=Client(oauth)
# print(str(client) +"Client")
#
# me = client.user(user_id='me').get()
# print('user_login: ' + me['login'])
#
# root_folder = client.folder(folder_id='315998749').get()
# print('folder owner: ' + root_folder.owned_by['login'])
# print('folder name: ' + root_folder['name'])


oauth2URL = 'https://app.box.com/api/oauth2/token'
refreshToken='bdVOnGs2t6wDfVDndZTAyBfJBQ2dfpTToRcf5ZZaZvEsj1k0ZcDcp1V7bHwjhSM0'
clientId='4qerinz9kgy7adw653wb90co0vg1drt8'
clientSecret='z0tvo8H3OqJR18Vga6zp9Ua1jYdAPF62'

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
refreshToken=newTokens['refresh_token']
print("New accessToken "+accessToken)
print("New refreshToken "+refreshToken)

# me = client.user(user_id='abhiram.natarajan@gmail.com').get()
# print('user_login: ' + me['login'])