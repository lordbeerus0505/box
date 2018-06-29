"""
Different functions required for angular
"""
#import uuid

from django.conf import settings
import json
from django.http import HttpResponse
from django.shortcuts import render
from yellowant import YellowAnt
#from django.urls import reverse
from ..yellowant_api.models import UserIntegration,BOX_Credentials
#from .forms import UserForm
#from django.contrib.auth import authenticate, login


#import requests
# Create your views here.


def index(request, path=""):
    """Index of the user Integration."""


    if request.user.is_authenticated:
        user_integrations = UserIntegration.objects.filter(user=request.user.id)
        #print(user_integration)
        # for user_integration in user_integrations:
        #     context["user_integrations"].append(user_integration)
    context = {"base_href": settings.BASE_HREF,
               "application_id": settings.YA_APP_ID,
               "user_integrations": []
               }

    print("returning from index")
    return render(request, "home.html", context)

def userdetails(request):
    """
    Returns the details of each user in a list.
    """
    print("user details")
    user_integrations_list = []
    if request.user.is_authenticated:
        print("authenticated")
        user_integrations = UserIntegration.objects.filter(user=request.user.id)

        for user_integration in user_integrations:
            #print (user_integration.yellowant_integration_invoke_name)
            print(str(user_integration.id)+"  user integration.id")
            smut = BOX_Credentials.objects.get(user_integration_id=user_integration.id)
            if smut.BOX_UPDATE_LOGIN_FLAG == True:
                print("TEST",smut.BOX_UPDATE_LOGIN_FLAG)
                smut = BOX_Credentials.objects.get(user_integration_id=user_integration.id)
                user_integrations_list.append(
                    {"user_invoke_name":user_integration.yellowant_integration_invoke_name,
                     "id":user_integration.id,
                     "app_authenticated":True, "is_valid":True})
            else: #user_integration.DoesNotExist:
                user_integrations_list.append({"user_invoke_name": user_integration.yellowant_integration_invoke_name,
                                               "id": user_integration.id, "app_authenticated":True, "is_valid":False})

    #print(user_integrations_list)
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")

def delete_integration(request, id=None):

    print("In delete_integration")

    print(id)

    print("user is ",request.user.id)

    access_token_dict = UserIntegration.objects.get(id=id)

    user_id = access_token_dict.user

    if user_id == request.user.id:



        access_token = access_token_dict.yellowant_integration_token

        user_integration_id = access_token_dict.yellowant_integration_id

        print(user_integration_id)

        url = "https://api.yellowant.com/api/user/integration/%s"%(user_integration_id)

        yellowant_user = YellowAnt(access_token=access_token)

        profile = yellowant_user.delete_user_integration(id=user_integration_id)

        response_json = UserIntegration.objects.get(yellowant_integration_token = access_token ).delete()

        print(response_json)

        return HttpResponse("successResponse", status=204)

    else:

        return HttpResponse("Not Authenticated", status=403)





def view_integration(request, id=None):
    """
    Function to View an integration when it is clicked.
    """
    #print("In view_integration")
    #print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    #print(user_integration_id)
    url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    #print(response_json)
    return HttpResponse("successResponse", status=200)
