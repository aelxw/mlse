
# coding: utf-8

# In[1]:


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
    teams = [{"name":team.find("a").text.strip(), "logo":team.find("img").attrs["src"]} for team in teams_li]
    return teams


# In[3]:


app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mlse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
http_server = WSGIServer(('', 2000), app)


# In[4]:


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


# In[5]:


class UserSchema(ma.Schema):
    class Meta:
        fields = ('fullname', 'email', 'role')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# In[6]:


class Team(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    logo = db.Column(db.String(500))
    division = db.Column(db.String(50))
    show = db.Column(db.Boolean)
    date = db.Column(db.Date)

    def __init__(self, name, division, logo):
        self.name = name
        self.division = division
        self.logo = logo
        self.show = False
        self.date = dt.today().date()


# In[7]:


class TeamSchema(ma.Schema):
    class Meta:
        fields = ('index', 'name', 'division', 'logo', 'date', 'show')
        
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

@app.route("/teams-get-all")
def get_nhl_teams():
    return jsonify(teams_schema.dump(Team.query.all()).data)

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
    index = req_data["index"]
    team = Team.query.get(index)
    
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
    team = Team.query.get(request.json["index"])
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


# In[ ]:


http_server.serve_forever()

