from flask import Flask
from flask import request
from flask import current_app
from flask import make_response
from flask import redirect, url_for, abort
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_bootstrap import Bootstrap

import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY']='jdlfd jdklf dlla ld2oq n'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

app_ctx = app.app_context()
app_ctx.push()

@app.route("/", methods=['GET', 'POST'])
def index():
	name = None
	age = None
	form = UserForm()
	if form.validate_on_submit():
		name = form.name.data
		age = form.age.data
		
		user = User(name = name, age = age)
		db.session.add(user)
		db.session.commit()

		form.name.data = ""
		form.age.data = ""
		return redirect(url_for(".user", name=name))
	return render_template("index.html", name=name, age = age, form=form)

@app.route("/user/<name>")
def user(name):
	return "<h1>hello, {}! </h1>".format(name)

class UserForm(FlaskForm):
	name = StringField('User: ', validators=[DataRequired()])
	age = IntegerField('age: ', validators=[NumberRange(min=1, max=120)])
	submit = SubmitField('Submit')

class User(db.Model):
	name = db.Column(db.String, nullable = False, primary_key = True)
	age = db.Column(db.Integer)	










	
