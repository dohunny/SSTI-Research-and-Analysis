from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask.templating import render_template_string
import uuid
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
    uid = Column(TEXT, primary_key=True)
    upw = Column(TEXT)
    message = Column(TEXT)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = str(uuid.uuid4())
db = init_db(app)

app.register_blueprint(app_route) 

@app.route('/', methods=["GET"])
def index():
    if not session.get('user'):
        return redirect(url_for('signin'))
    user = session.get('user')
    return render_template("index.html", uid=user['uid'], message=user['message'])
      
@app.route("/detail")
def page():
    if not session.get('user'):
        return redirect(url_for('signin'))
    memo = session.get('user')['message']
    output = Jinja2.from_string(render_template_string(memo)).render()
    return output

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        if session.get('user'):
            return redirect(url_for('index'))
        return render_template('signin.html')
    else:
        uid = str(request.form['uid'])
        upw = str(request.form['upw'])
        res = Notes.query.filter_by(uid=uid, upw=upw).first()
        if res is not None:
            session['user'] = {"uid":res., "message":message}
            return redirect(url_for('index'))
        else:
            flash("Wrong ID or PW")
            return redirect(url_for('signin'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    else:
        uid = str(request.form['uid'])
        upw = str(request.form['upw'])
        message = str(request.form['message'])
        res = Notes.query.filter_by(uid=uid).first()
        if res is not None:
            flash("Your ID already exists")
            return redirect(url_for('signin'))
        notes = Notes(
            uid = uid, 
            upw = upw,
            message = message
        )
        db.session.add(notes)
        db.session.commit()
        session['user'] = {"uid":uid, "message":message}
        flash("Registeration Success!")
        return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))

if __name__ == '__main__': 
	# app.run(host='0.0.0.0')
	app.run(host='0.0.0.0', port=40012, debug=True)
