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

def impressum(request):
    return render(request, "whatToWatchApp/impressum.html")

def anime(request):
    name = request.GET.get('name', '')
    # if no name is given go to index
    if name == '':
        return render(request, "whatToWatchApp/index.html", context={"user_found": True, "user_valid": False})

    # Indicies for myanimelist
    watchStatusDict = {'watching': 1, 'completed': 2, 'onhold': 3, 'dropped': 4, 'plantowatch': 6, 'all': 7}

    # Get checkbox entries
    watching = request.GET.get('watching', 'false')
    completed = request.GET.get('completed', 'false')
    onhold = request.GET.get('onhold', 'false')
    dropped = request.GET.get('dropped', 'false')
    plantowatch = request.GET.get('plantowatch', 'false')

    statusList = []

    
    # Check for legit values and put all selected checkboxes in statusList
    watchStatus = [watching, completed, onhold, dropped, plantowatch]
    watchString = ['watching', 'completed', 'onhold', 'dropped', 'plantowatch']
    for i in range(0, len(watchStatus)):
        if watchStatus[i] == 'true':
            statusList.append(watchStatusDict[watchString[i]])
        elif watchStatus[i] not in ['true', 'false']:
            print(watchStatus[i], type(watchStatus[i]))
            return render(request, "whatToWatchApp/index.html")

    # Check if the profile is valid
    URL = 'https://myanimelist.net/profile/' + str(name)
    page = webrequests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    userIsFound= True if len(soup.find_all("div", {"class": "error404"})) == 0 else False

    if not userIsFound:
        return render(request, "whatToWatchApp/index.html", context={"user_found": False, "user_name": name})

    # If no checkbox is selected go to index
    if len(statusList) == 0:
        return render(request, "whatToWatchApp/index.html")
    elif len(statusList) == 5:
        statusList = [7]

    results = []
    # For each clicked checkbox get the anime entries from myanimelist
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
    
    # If there are no anime entries go to index
    if len(results) == 0:
        return render(request, "whatToWatchApp/index.html", context={"user_no_entries": False, "user_name":name})
    
    # Choose a random entry from the found ones
    result = random.choice(results)
    animeTitle = result[0]
    animeURL = 'https://myanimelist.net' + result[1]
    print("Dein Random Anime ist:", animeTitle, animeURL)
    
    # Get the image of the selected anime
    session = HTMLSession()
    response = session.get(animeURL)
    imageURL = response.html.find('td.borderClass div div a img', first=True).attrs['data-src']

    # Get the synopsis of the selected anime
    synopsis = response.html.find('p[itemprop="description"]', first=True).html
    session.close()

    return render(request, "whatToWatchApp/anime.html", {"title": animeTitle,
                                                         "titleURL": animeURL,
                                                         "image": imageURL,
                                                         "synopsis": synopsis})