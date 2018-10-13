
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
import jwt
import os
import datetime
from datetime import datetime as dt


# In[ ]:


def scrape_nhl_teams():
    teams_url = "http://www.sportslogos.net/teams/list_by_league/1/National_Hockey_League/NHL/logos/"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_li = soup.find(attrs={"id":"team"}).find(attrs={"class":"logoWall"}).findAll("li")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NHL"} for team in teams_li]
    return teams

def insert_nhl_teams():
    nhl_teams = scrape_nhl_teams()
    for team in nhl_teams:
        t = Team(team["name"], team["division"], team["logo"])
        db.session.add(t)
        db.session.commit()

def scrape_nba_teams():
    teams_url = "http://www.nba.com/teams"
    res = requests.get(teams_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    teams_div = soup.find("section", attrs={"id":"block-teamlistblock"}).find("div", attrs={"class":"team__list_wrapper"}).findAll("div")
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"], "division":"NBA"} for team in teams_div]
    return teams

def insert_nba_teams():
    nba_teams = scrape_nba_teams()
    for team in nba_teams:
        t = Team(team["name"], team["division"], team["logo"])
        db.session.add(t)
        db.session.commit() 


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


class User(db.Model):
    email = db.Column(db.String(250), primary_key=True, unique=True)
    fullname = db.Column(db.String(250))
    role = db.Column(db.String(150))
    password = db.Column(db.String(250))

    def __init__(self, email, password, fullname):
        self.email = email
        self.role = "user"
        self.password = password
        self.fullname = fullname


# In[ ]:


class UserSchema(ma.Schema):
    class Meta:
        fields = ('fullname', 'email', 'role')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# In[ ]:


class Team(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    logo = db.Column(db.String(500))
    division = db.Column(db.String(50))

    def __init__(self, name, division, logo):
        self.name = name
        self.division = division
        self.logo = logo


# In[ ]:


class TeamSchema(ma.Schema):
    class Meta:
        fields = ('team_id', 'name', 'division', 'logo')
        
team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


# In[ ]:


@app.route("/user-create", methods=["POST"])
def sign_up():
    email = request.json['email']
    password = request.json['password']
    fullname = request.json['fullName']
    confirmpassword = request.json['confirmPassword']

    if(password == confirmpassword):
        new_user = User(email, password, fullname)
        db.session.add(new_user)
        db.session.commit()
        payload = eval(user_schema.dumps(User.query.get(email)).data)
        encoded = jwt.encode(payload, 'secret', algorithm='HS256').decode("utf-8")
        return json.dumps({"token":encoded})
    else:
        return "", 500

@app.route("/user-get", methods=["POST"])
def user_detail():
    user = User.query.get(email)
    return user_schema.jsonify(user)

@app.route("/user-get-all", methods=["GET"])
def get_user():
    return jsonify(users_schema.dump(User.query.all()).data)

@app.route("/role-update", methods=["POST"])
def user_update():
    req_data = request.json
    email = req_data["email"]
    user = User.query.get(email)
    
    if(req_data["role"]):
        user.role = req_data["role"]

    db.session.commit()
    return user_schema.jsonify(user)

@app.route("/user-delete", methods=["POST"])
def user_delete():
    user = User.query.get(request.json["email"])
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route("/teams-get-nhl")
def get_nhl_teams():
    return jsonify(teams_schema.dump(Team.query.filter_by(division="NHL")).data)

@app.route("/teams-get-nba")
def get_nba_teams():
    return jsonify(teams_schema.dump(Team.query.filter_by(division="NBA")).data)

@app.route("/team-create", methods=["POST"])
def team_create():
    req_data = request.json
    team = Team("", "", "")
    if(req_data["division"]):
        team.division = req_data["division"]
    if(req_data["logo"]):
        team.logo = req_data["logo"]
    if(req_data["name"]):
        team.name = req_data["name"]
        
    db.session.add(team)
    db.session.commit()
    return team_schema.jsonify(team)

@app.route("/team-update", methods=["POST"])
def team_update():
    req_data = request.json
    team_id = req_data["team_id"]
    team = Team.query.get(team_id)
    
    team.show = req_data["show"]
    if(req_data["date"]):
        team.date = dt.strptime(req_data["date"], '%Y-%m-%d').date()
    if(req_data["division"]):
        team.division = req_data["division"]
    if(req_data["logo"]):
        team.logo = req_data["logo"]
    if(req_data["name"]):
        team.name = req_data["name"]

    db.session.commit()
    return team_schema.jsonify(team)

@app.route("/team-delete", methods=["POST"])
def team_delete():
    team = Team.query.get(request.json["team_id"])
    db.session.delete(team)
    db.session.commit()
    return team_schema.jsonify(team)


@app.route("/login", methods=["POST"])
def authenticate():
    req_data = request.json
    email = req_data["email"]
    password = req_data["password"]
    user = User.query.get(email)
    if(user):
        if(user.password == password):
            payload = eval(user_schema.dumps(user).data)
            encoded = jwt.encode(payload, 'secret', algorithm='HS256').decode("utf-8")
            return json.dumps({"token":encoded})
        else:
            return "", 500
    else:
        return "", 500

@app.route("/shutdown")
def shutdown():
    http_server.stop()
    return "Server shutting down..."


# In[97]:


http_server.serve_forever()

