from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Context, loader

from bs4 import BeautifulSoup
import requests as webrequests

# Create your views here.
def index(request):
    return render(request, "whatToWatchApp/index.html")

def anime(request):
    name = request.GET.get('name', '')
    if name is '':
        return render(request, "whatToWatchApp/index.html")

    watchStatusDict = {'watching': 1, 'completed': 2, 'onhold': 3, 'dropped': 4, 'plantowatch': 6, 'all': 7}

    watching = request.GET.get('watching', 'false')
    completed = request.GET.get('completed', 'false')
    onhold = request.GET.get('onhold', 'false')
    dropped = request.GET.get('dropped', 'false')
    plantowatch = request.GET.get('plantowatch', 'false')

    statusList = []

    watchStatus = [watching, completed, onhold, dropped, plantowatch]
    for var in watchStatus:
        if var is 'true':
            statusList.append(watchStatusDict[var])
        elif var not in ['true', 'false']:
            print(var, type(var))
            return render(request, "whatToWatchApp/index.html")

    URL = 'https://myanimelist.net/profile/' + str(name)
    page = webrequests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    userIsValid = True if len(soup.find_all("div", {"class": "error404"})) == 0 else False

    status = -1
    if len(statusList) == 1:
        status = statusList[0]
    elif len(statusList) == 5:
        status = watchStatusDict['all']

    if status is not -1:
        URL = 'https://myanimelist.net/animelist/' + name + '?status=' + status
        page = webrequests.get(URL)
    else:
        pass

    return render(request, "whatToWatchApp/anime.html")