from flask import Flask, flash, render_template, request, session, redirect
from flask.templating import render_template_string
from sklearn.utils import resample
from route.app_route import app_route 
from jinja2 import Environment
from sqlalchemy import Column, TEXT
from sqlalchemy_utils import UUIDType
from flask_sqlalchemy import SQLAlchemy

Jinja2 = Environment()
app = Flask(__name__)

FLAG = "FLAG{YOU_KNOW_SSTI!_WELL_DONE!}"

# DB
db = SQLAlchemy()
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db

class Notes(db.Model):
    __tablename__ = 'notes'
    uuid = Column(UUIDType(binary=False), primary_key=True)
    uid = Column(TEXT)
    upw = Column(TEXT)
    message = Column(TEXT)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = init_db(app)

app.register_blueprint(app_route) 

@app.route('/', methods=["GET","POST"])
def index():
    if not session.get('uid'):
        signin()
    if request.method == "GET":
        return render_template('index.html', memo=memo)
    else:
        return redirect("/page")
    
@app.route("/page")
def page():
    memo = request.values.get('memo','')
    output = Jinja2.from_string(render_template_string(memo)).render()
    return output

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        if not session.get('uid'):
            return render_template('signin.html')
        else:
            return redirect("/page")
    else:
        uid = request.form['uid']
        upw = request.form['upw']
        res = Notes.query.filter_by(uid=uid, upw=upw).first()
        if res is not None:
            session['uid'] = uid
            return redirect("/page")
        else:
            flash("Wrong ID or PW")
            return redirect("/signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if not session.get('uid'):
            return render_template('signup.html')
        else:
            return redirect("/page")
    else:
        uid = request.form['uid']
        upw = request.form['upw']
        message = request.form['message']
        res = Notes.query.filter_by(uid=uid).first()
        if res is not None:
            flash("Your ID already exists")
            return redirect("/signup")
        else:
            notes = Notes(
                uid = str(uid), 
                upw = str(upw),
                message = str(message)
            )
            db.session.add(notes)
            db.session.commit()
            session['uid'] = uid
            return redirect("/page")


if __name__ == '__main__': 
	# app.run(host='0.0.0.0')
	app.run(host='0.0.0.0', port=40012)
