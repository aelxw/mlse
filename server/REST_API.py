#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import the neccessary libraries

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
    # Scrape web page to get NHL team data
    teams_url = "http://www.sportslogos.net/teams/list_by_league/1/National_Hockey_League/NHL/logos/"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_li = soup.find(attrs={"id":"team"}).find(attrs={"class":"logoWall"}).findAll("li")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NHL"} for team in teams_li]
    return teams

def scrape_nba_teams():
    # Scrape web page to get NBA team data
    teams_url = "http://www.nba.com/teams"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_div = soup.find("section", attrs={"id":"block-teamlistblock"}).find("div", attrs={"class":"team__list_wrapper"}).findAll("div")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NBA"} for team in teams_div]
    return teams


# In[ ]:


# Set up REST API and database

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/mlse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
http_server = WSGIServer(('localhost', 2000), app)


# There are only __two__ tables in the SQLite database:
# 1. Team (data for NHL/NBA teams)
# > - name (team name)
# > - logo (url link to picture of team icon)
# > - division (NHL/NBA)
#             
# 2. Prev (previous rank for each employee)
# > - email (email of employee)
# > - rank (rank employee got in the last matching round)
# > - division (NHL/NBA)

# In[ ]:


# Team table schema object

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


# Prev table schema object

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


# Functions to insert scraped team data into the SQLite database

def insert_nhl_teams():
    # Insert NHL team data into SQLite database
    nhl_teams = scrape_nhl_teams()
    if(len(nhl_teams) > 0):
        Team.query.filter_by(division="NHL").delete()
        for team in nhl_teams:
            t = Team(team["name"], team["division"], team["logo"])
            db.session.add(t)
        db.session.commit()
    return len(nhl_teams)

def insert_nba_teams():
    # Insert NBA team data into SQLite database
    nba_teams = scrape_nba_teams()
    if(len(nba_teams) > 0):
        Team.query.filter_by(division="NBA").delete()
        for team in nba_teams:
            t = Team(team["name"], team["division"], team["logo"])
            db.session.add(t)
        db.session.commit()
    return len(nba_teams)


# In[ ]:


# Endpoints for the REST API

@app.route("/teams-get")
def get_teams():
    # Return team data from database
    return jsonify(teams_schema.dump(Team.query).data)

@app.route("/teams-update")
def update_teams():
    # Overwrite team data in the database if new teams join the NHL/NBA
    # This is assuming: 
    # 1. The websites update the teams on their website
    # 2. The structure of the websites (the HTML) doesn't change
    nhl = insert_nhl_teams()
    nba = insert_nba_teams()
    return "NHL: {} updated, NBA: {} updated".format(nhl, nba)

@app.route("/match", methods=["POST"])
def run_matching():
    # Run the matching
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
    
    # Use historical data
    #prev_rankings = pd.DataFrame.from_dict(temp, orient="index")
    
    bo = BO(data, ticket_capacity, prev_rankings=None)
    bo.optimize()
    
    return jsonify(bo.sol)

@app.route("/save-ranks", methods=["POST"])
def saveRanks():
    # Updates the ranks in the Prev table
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
    # Shuts down the REST API
    http_server.stop()
    return "Server shutting down..."


# In[ ]:


# Run the server
http_server.serve_forever()

