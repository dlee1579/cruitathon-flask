from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import json
from ast import literal_eval
from graph import *
from os import environ
import datetime

app = Flask("__main__")
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('URI_DB')
db = SQLAlchemy(app)

class Teams(db.Model):
    def __init__(cls, classname, bases, dict_):
        super().__init__(classname, bases, dict_)
        pass
    
    __tablename__ = "Teams"
    team_id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String)
    conference = db.Column(db.String)
    mascot = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)

class Recruits(db.Model):
    __tablename__ = "Recruits"
    player_id = db.Column(db.Integer, primary_key =  True)
    name = db.Column(db.String)
    team = db.Column(db.String)
    position = db.Column(db.String)
    score = db.Column(db.Numeric)
    hometown = db.Column(db.String)
    state = db.Column(db.String)

class Offers(db.Model):
    __tablename__ = "Offers"
    offer_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer)
    offer = db.Column(db.String)

class User_Comments(db.Model):
    __tablename__ = "User_Comments"
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_user = db.Column(db.String)
    team = db.Column(db.String)
    text = db.Column(db.String)
    time_submitted = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with open("Colors.json") as json_file:
    colors = json.load(json_file)

@app.route('/')
def home():
    # teams = db.session.query(Teams.team, Teams.conference).all()
    # print('called from React')
    # return jsonify([{"team": r[0], "conference": r[1]} for r in teams])
    return {"message": "Cruitathon Home Page"}

@app.route("/team/<team_selected>", methods=["GET"])
def team(team_selected):
    recruits = db.session.query(Recruits.player_id, Recruits.name, Recruits.state, Recruits.position, Recruits.score).filter(Recruits.team == team_selected)

    recruits_df = pd.read_sql(recruits.statement, db.engine)
    commit_count = int(recruits_df.name.count())
    avg_score = round(recruits_df.score.mean(), 5)
    
    print(colors[team_selected]["colors"][0])

    pos_dist = recruits_df.groupby(by="position").count().reset_index().sort_values("player_id", ascending=False)[["position", "player_id"]]
    state_dist = recruits_df.groupby(by="state").count().reset_index().sort_values("player_id")[["state", "player_id"]]

    competition_query = '''
    select team, offer, count(offer) as offer_count from 
    (
    select o.player_id, team, offer from "Offers" o
    join "Recruits" r on o.player_id =r.player_id
    where team = '{}'
    and team <> offer
    ) t
    group by team, offer
    order by offer_count desc
    limit 8
    '''
    comp_dist = pd.read_sql_query(competition_query.format(team_selected), db.engine)

    comments_query = db.session.query(User_Comments.comment_id, User_Comments.comment_user, User_Comments.team, User_Comments.text, User_Comments.time_submitted).filter(User_Comments.team == team_selected).all()
    comments_json = [{"comment_id": u.comment_id, "comment_user": u.comment_user, "team":u.team, "text": u.text, "time_submitted": u.time_submitted} for u in comments_query]

    return {
    "team_aggregate_stats": {"team" : team_selected,
    "commit_count": commit_count,
    "avg_score": avg_score,
    "color_primary": colors[team_selected]["colors"][0],
    "color_secondary": colors[team_selected]["colors"][1]},
    "team_position_stats": literal_eval(pos_dist_plot(pos_dist)),
    "team_state_stats": literal_eval(state_dist_plot(state_dist)),
    "team_competition_stats": literal_eval(competition_plot(comp_dist)),
    "comments_list": comments_json
    }

# @app.route('/submit/team=<team>/text=<text>', methods=["GET"])
# def submit_comment(team, text):
#     comment = User_Comments(comment_user="test user", team=team, text=text)
#     db.session.add(comment)
#     db.session.commit()
#     comments_query = db.session.query(User_Comments.comment_id, User_Comments.comment_user, User_Comments.team, User_Comments.text, User_Comments.time_submitted).filter(User_Comments.team == team).all()

#     return jsonify([{"comment_id": u.comment_id, "comment_user": u.comment_user, "team":u.team, "text": u.text, "time_submitted": u.time_submitted} for u in comments_query])

@app.route('/submit', methods=['POST'])
def submit_comment():
    team = request.json['team']['team']
    text = request.json['text']['text']
    comment = User_Comments(comment_user="test user", team=team, text=text)
    db.session.add(comment)
    db.session.commit()

    comments_query = db.session.query(User_Comments.comment_id, User_Comments.comment_user, User_Comments.team, User_Comments.text, User_Comments.time_submitted).filter(User_Comments.team == team).all()
    return jsonify([{"comment_id": u.comment_id, "comment_user": u.comment_user, "team":u.team, "text": u.text, "time_submitted": u.time_submitted} for u in comments_query])


if __name__ == "__main__":
    app.run(debug=True)
