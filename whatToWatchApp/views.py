from django.http.response import FileResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Context, loader

from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests as webrequests
import random, time

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
    watchString = ['watching', 'completed', 'onhold', 'dropped', 'plantowatch']
    for i in range(0, len(watchStatus)):
        if watchStatus[i] == 'true':
            statusList.append(watchStatusDict[watchString[i]])
        elif watchStatus[i] not in ['true', 'false']:
            print(watchStatus[i], type(watchStatus[i]))
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
        URL = 'https://myanimelist.net/animelist/' + str(name) + '?status=' + str(status)

        session = HTMLSession()
        response = session.get(URL)
        table = response.html.find('.list-table', first=True)
        table = table.attrs["data-items"]

        table = table.replace('null', 'None')
        table = table.replace('true', 'True')
        table = table.replace('false', 'False')

        table = eval(table)
        result = random.choice(table)
        print("Dein Random Anime ist:", result['anime_title'], result['anime_url'].replace('\\', ''), result['anime_image_path'].replace('\\', ''))
        
        URL = 'https://myanimelist.net' + result['anime_url'].replace('\\', '')
        session = HTMLSession()
        response = session.get(URL)
        imageURL = response.html.find('td.borderClass div div a img', first=True).attrs['data-src']

    else:
        return render(request, "whatToWatchApp/index.html")

    return render(request, "whatToWatchApp/anime.html", {"title": result['anime_title'], "image": imageURL})