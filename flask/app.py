from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask.templating import render_template_string
import uuid
from route.app_route import app_route 
from jinja2 import Environment
from sqlalchemy import Column, TEXT
from flask_sqlalchemy import SQLAlchemy

Jinja2 = Environment()
app = Flask(__name__)

FLAG = "FLAG{YOU_KNOW_SSTI!_WELL_DONE!}"

# To Do: DB파일 30분마다 초기화

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
    if session.get('user'):
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('signin.html')
    else:
        uid = str(request.form['uid'])
        upw = str(request.form['upw'])
        res = Notes.query.filter_by(uid=uid, upw=upw).first()
        if res is not None:
            session['user'] = {"uid":res.uid, "message":res.message}
            return redirect(url_for('index'))
        else:
            flash("Wrong ID or PW")
            return redirect(url_for('signin'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        uid = str(request.form['uid']).strip()
        upw = str(request.form['upw']).strip()
        message = str(request.form['message'])
        if not uid or not upw or not message:
            flash("No data")
            return redirect(url_for('signup'))
        res = Notes.query.filter_by(uid=uid).first()
        if res is not None:
            flash("Your ID already exists")
            return redirect(url_for('signup'))
        notes = Notes(
            uid = uid, 
            upw = upw,
            message = message
        )
        db.session.add(notes)
        db.session.commit()
        flash("Registeration Success!")
        return redirect(url_for('signin'))

@app.route('/edit', methods=['GET','POST'])
def edit():
    if not session.get('user'):
        return redirect(url_for('signin'))
    if request.method == "POST":
        old_pw = str(request.form['opw'])
        new_pw = str(request.form['npw'])
        message = str(request.form['message'])
        if (old_pw and new_pw) or message:
            if old_pw and new_pw: 
                res = Notes.query.filter_by(uid=session.get('user')['uid'], upw=old_pw).first()
                if res is None:
                    flash("Wrong ID or PW")
                    return redirect(url_for('edit'))
                res.upw = new_pw
            if message is not None:
                res = Notes.query.filter_by(uid=session.get('user')['uid']).first()
                res.message = message
            db.session.commit()
            session['user'] = {"uid":session.get('user')['uid'], "message":message}
            return redirect(url_for('index'))

        flash("No Data")
        return redirect(url_for('edit'))

    return render_template('edit.html', uid=session.get('user')['uid'], ms=session.get('user')['message'])
        

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))

if __name__ == '__main__': 
	# app.run(host='0.0.0.0')
	app.run(host='0.0.0.0', port=40012, debug=True)
