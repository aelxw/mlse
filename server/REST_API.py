
# coding: utf-8

# In[1]:


from flask import Flask, json, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests


# In[2]:


def gale_shapely(E):
    # n employees, m tickets
    T = np.random.rand(E.shape[0], E.shape[1])
    M = np.zeros(T.shape)
    while M.sum() < np.min(E.shape):
        un_i = np.linspace(0, M.shape[0]-1, M.shape[0])[M.sum(axis=1) == 0]
        if un_i.size > 0:
            x = int(un_i[0])
            y = E[x, :].argmin()
            E[x,y] = np.max(E.shape)+1
            if M[:, y].sum() == 0:
                M[x, y] = 1
            elif T[x, y] < T[M[:, y].argmax(), y]:
                M[:, y] = 0
                M[x, y] = 1
    return M

def scrape_nhl_teams():
    teams_url = "http://www.sportslogos.net/teams/list_by_league/1/National_Hockey_League/NHL/logos/"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_li = soup.find(attrs={"id":"team"}).find(attrs={"class":"logoWall"}).findAll("li")
    teams = [{"team":team.find("a").text.strip(), "logo":team.find("img").attrs["src"]} for team in teams_li]
    return teams


# In[7]:


app = Flask(__name__)
CORS(app)
http_server = WSGIServer(('', 2000), app)

nhl_teams = scrape_nhl_teams()

@app.route("/nhl-teams")
def getNHLTeams():
    return json.dumps(nhl_teams)

@app.route("/login", methods=["POST"])
def authenticate():
    req_data = request.json
    if(req_data["email"] == "a" and req_data["password"] == "b"):
        return json.dumps(True)
    else:
        return json.dumps(False)

@app.route("/shutdown")
def shutdown():
    http_server.stop()
    return "Server shutting down..."


# In[ ]:


http_server.serve_forever()

