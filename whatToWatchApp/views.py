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
    return render(request, "whatToWatchApp/index.html", context={"user_found": True, "user_valid": True})

def anime(request):
    name = request.GET.get('name', '')
    if name == '':
        return render(request, "whatToWatchApp/index.html", context={"user_found": True, "user_valid": False})

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
    userIsFound= True if len(soup.find_all("div", {"class": "error404"})) == 0 else False

    if not userIsFound:
        return render(request, "whatToWatchApp/index.html", context={"user_found": False, "user_valid": True, "user_name": name})

    if len(statusList) == 0:
        return render(request, "whatToWatchApp/index.html", context={"user_found": True, "user_valid": True})
    elif len(statusList) == 5:
        statusList = [7]

    results = []
    for status in statusList:
        URL = 'https://myanimelist.net/animelist/' + str(name) + '?status=' + str(status)

        session = HTMLSession()
        response = session.get(URL)
        table = response.html.find('.list-table', first=True)
        table = table.attrs["data-items"]

        table = table.replace('null', 'None')
        table = table.replace('true', 'True')
        table = table.replace('false', 'False')

        table = eval(table)
        for entry in table:
            results.append((entry['anime_title'], entry['anime_url'].replace('\\', '')))
    
    result = random.choice(results)
    animeTitle = result[0]
    animeURL = 'https://myanimelist.net' + result[1]
    print("Dein Random Anime ist:", animeTitle, animeURL)
    
    session = HTMLSession()
    response = session.get(animeURL)
    imageURL = response.html.find('td.borderClass div div a img', first=True).attrs['data-src']

    synopsis = response.html.find('p[itemprop="description"]', first=True).html
    session.close()

    return render(request, "whatToWatchApp/anime.html", {"title": animeTitle,
                                                         "titleURL": animeURL,
                                                         "image": imageURL,
                                                         "synopsis": synopsis})