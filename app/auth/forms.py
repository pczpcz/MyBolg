from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, ValidationError, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from ..models import User, Role

class UserForm(FlaskForm):
	name = StringField('username:', validators=[DataRequired()])
	password = StringField("password:", validators=[DataRequired()])
	remember_me = BooleanField("Keep me logged in");
	submit = SubmitField("submit")

class RegisterForm(FlaskForm):
	name = StringField("Username:", validators=[DataRequired()])
	email = StringField("Email:", validators=[DataRequired()])
	
	password = PasswordField("Password", validators=[DataRequired(), \
		EqualTo('password2', message='Passwords must match')])
	password2 = PasswordField("Confirm password", validators=[DataRequired()])

	submit = SubmitField("Register")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self, field):
		if User.query.filter_by(name=field.data).first():
			raise ValidationError('Username already in use.')

class UserEditForm(FlaskForm):
	name = StringField('username:', validators=[DataRequired()])
	location = StringField('location:', validators=[DataRequired()])
	about_me = TextAreaField('about_me:', validators=[DataRequired()])
	submit = SubmitField('submit')

class AdminEditForm(UserEditForm):
	conformed = BooleanField('conformed')
	phone_number = StringField('phone_numbe')
	age = IntegerField('age:')
	email = StringField('email:')
	role = SelectField('Role', coerce=int)

	def __init__(self, user):
		self.role.choices = [(role_id, role_name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and User.query.filter_by(name=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self, field):
		if User.query.filter_by(name=field.data).first():
			raise ValidationError('Username already in use.')


	



