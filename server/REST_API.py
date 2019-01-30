
# coding: utf-8

# In[ ]:


from flask import Flask, json, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from gevent.pywsgi import WSGIServer

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import datetime
from datetime import datetime as dt

from Models import BO


# In[ ]:


def scrape_nhl_teams():
    teams_url = "http://www.sportslogos.net/teams/list_by_league/1/National_Hockey_League/NHL/logos/"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_li = soup.find(attrs={"id":"team"}).find(attrs={"class":"logoWall"}).findAll("li")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NHL"} for team in teams_li]
    return teams

def scrape_nba_teams():
    teams_url = "http://www.nba.com/teams"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_div = soup.find("section", attrs={"id":"block-teamlistblock"}).find("div", attrs={"class":"team__list_wrapper"}).findAll("div")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NBA"} for team in teams_div]
    return teams

def insert_nhl_teams():
    nhl_teams = scrape_nhl_teams()
    if(len(nhl_teams) > 0):
        Team.query.filter_by(division="NHL").delete()
        for team in nhl_teams:
            t = Team(team["name"], team["division"], team["logo"])
            db.session.add(t)
        db.session.commit()
    return len(nhl_teams)

def insert_nba_teams():
    nba_teams = scrape_nba_teams()
    if(len(nba_teams) > 0):
        Team.query.filter_by(division="NBA").delete()
        for team in nba_teams:
            t = Team(team["name"], team["division"], team["logo"])
            db.session.add(t)
        db.session.commit()
    return len(nba_teams)


# In[ ]:


app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/mlse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
http_server = WSGIServer(('', 2000), app)


# In[ ]:


class Team(db.Model):
    name = db.Column(db.String(250), primary_key=True)
    logo = db.Column(db.String(500))
    division = db.Column(db.String(50))

    def __init__(self, name, division, logo):
        self.name = name
        self.division = division
        self.logo = logo

class TeamSchema(ma.Schema):
    class Meta:
        fields = ('name', 'division', 'logo')
        
team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


# In[ ]:


class Prev(db.Model):
    email = db.Column(db.String(250), primary_key=True)
    division = db.Column(db.String(20), primary_key=True)
    rank = db.Column(db.INTEGER())
    
    def __init__(self, email, division, rank):
        self.email = email
        self.division = division
        self.rank = rank

class PrevSchema(ma.Schema):
    class Meta:
        fields = ('email', 'division', 'rank')

prev_schema = PrevSchema()
prevs_schema = PrevSchema(many=True)


# In[ ]:


@app.route("/teams-get")
def get_teams():
    return jsonify(teams_schema.dump(Team.query).data)

@app.route("/teams-update")
def update_teams():
    nhl = insert_nhl_teams()
    nba = insert_nba_teams()
    return "NHL: {} updated, NBA: {} updated".format(nhl, nba)

@app.route("/match", methods=["POST"])
def run_matching():
    req_data = request.json
    responses = req_data[0]
    ticket_capacity = req_data[1]
    division = req_data[2]
    
    data = pd.DataFrame.from_dict(responses, orient="index")
    
    prev_table = {}
    for o in prevs_schema.dump(Prev.query.filter_by(division=division)).data:
        prev_table[o["email"]] = o["rank"]
    
    temp = {}
    for email in data.index:
        if email not in prev_table:
            temp[email] = 1
            db.session.add(Prev(email, division, 1))
        else:
            temp[email] = prev_table[email]
    db.session.commit()
    prev_rankings = pd.DataFrame.from_dict(temp, orient="index")
    
    bo = BO(data, ticket_capacity, prev_rankings)
    bo.optimize()
    
    print(bo.sol)
    
    return jsonify(bo.sol)

@app.route("/save-ranks", methods=["POST"])
def saveRanks():
    req_data = request.json
    ranks = req_data["ranks"]
    division = req_data["division"]
    for email in ranks:
        p = Prev.query.get((email, division))
        p.rank = int(ranks[email])
    db.session.commit()
    return "Updated"

@app.route("/shutdown")
def shutdown():
    http_server.stop()
    return "Server shutting down..."


# In[ ]:


http_server.serve_forever()

