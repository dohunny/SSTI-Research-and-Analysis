from flask import Flask, render_template, request
from flask.templating import render_template_string
from route.app_route import app_route 
from jinja2 import Environment

Jinja2 = Environment()
app = Flask(__name__)

FLAG = "FLAG{YOU_KNOW_SSTI!_WELL_DONE!}"

app.register_blueprint(app_route) 

@app.route('/', methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template('index.html', memo=memo)
    else:
        page()
    

@app.route("/page")
def page():
    memo = request.values.get('memo','')
    output = Jinja2.from_string(render_template_string(memo)).render()
    return output


if __name__ == '__main__': 
	app.run(host='0.0.0.0')
