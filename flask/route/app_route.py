from flask import Flask, render_template, request, Blueprint
from flask.templating import render_template_string
from jinja2 import Environment, Template

Jinja2 = Environment()
app_route = Blueprint('first_route',__name__)

@app_route.route('/')
def index():
   memo = request.args.get('memo','')
   # output = Jinja2.from_string(memo).render()
   return render_template("index.html", memoTemp=memo)