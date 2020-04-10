from flask import Flask
from flask import request
from flask import current_app
from flask import make_response
from flask import redirect, url_for, abort
from flask import render_template
from flask_wtf import FlaskForm
from wtforms imports StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app_ctx = app.app_context()
app_ctx.push()

@app.route("/")
def index():
	name = request.args.get("name")
	user_agent = request.headers.get("User_Agent")

	return "<h1>hello world!, my name is {} from {}</h1></b> responed by {}" \
		.format(name, user_agent, current_app.name)

@app.route("/user/<name>")
def user(name):
	response = make_response("<h2>response from server</h2>")
	#abort(404)
	#return redirect(url_for(".index"))
	usr_info = ["zhangsan", 20]
	return render_template("index.html", name=name, usr_info=usr_info)
