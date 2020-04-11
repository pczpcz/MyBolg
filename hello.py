from flask import Flask
from flask import request
from flask import current_app
from flask import make_response
from flask import redirect, url_for, abort
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app_ctx = app.app_context()
app_ctx.push()
bootstrap = Bootstrap(app)
app.config['SECRET_KEY']='jdlfd jdklf dlla ld2oq n'

@app.route("/", methods=['GET', 'POST'])
def index():
	name = None
	form = User()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ""
		return redirect(url_for(".user", name=name))
	return render_template("index.html", name=name, form=form)

@app.route("/user/<name>")
def user(name):
	return "<h1>hello, {}! </h1>".format(name)

class User(FlaskForm):
	name = StringField('User: ', validators=[DataRequired()])
	submit = SubmitField('Submit')










	
