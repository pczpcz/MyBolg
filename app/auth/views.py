from . import auth
from flask import render_template, redirect, url_for, flash, request
from .forms import UserForm, RegisterForm, UserEditForm, AdminEditForm
from ..models import User, Post
from flask_login import login_user, logout_user, login_required
from .. import db
from ..email import send_mail
from flask_login import current_user
from ..decorators import permission_required, admin_required

@auth.route("/login", methods=['GET', 'POST'])
def login():
	form = UserForm()
	if form.validate_on_submit():
		user = User.query.filter_by(name=form.name.data).first()
		if user and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for("main.index"))
	return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
	logout_user()
	flash('you have been logged out.')
	return redirect(url_for('main.index'))

@auth.route("/register", methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(name=form.name.data, email=form.email.data)
		user.password = form.password.data
		user.md5_hash = user.get_md5hash()
		
		db.session.add(user)
		db.session.commit()
		
		token = user.generate_confirmation_token()
		send_mail(user.email, 'confirm your accout', 'mail/confirm', token=token, user=user)

		flash("you can login now!")
		return redirect(url_for("auth.login"))
	return render_template("register.html", form=form)

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.update_logintime()	
		if not current_user.confirmed \
				and request.endpoint \
				and request.blueprint != 'auth' \
				and request.endpoint != 'static': 
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('unconfirmed.html')

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		db.session.commit()
		return redirect(url_for('main.index'))
	else:
		return redirect(url_for("main.index"))

@auth.route("/confirm")
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_mail(user.email, 'confirm your accout', 'mail/confirm', token=token,user=current_user)

	return redirect(url_for("main.index"))


@auth.route("/user/<username>")
@login_required
def user_info(username):
	user = User.query.filter_by(name=username).first()
	posts = user.posts.order_by(Post.post_time.desc())
	return render_template("user_info.html", user=user, posts=posts)

@auth.route("/user/useredit", methods=['GET', 'POST'])
@login_required
def useredit():
	form = UserEditForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data

		db.session.add(current_user._get_current_object())
		db.session.commit()
		return redirect(url_for('.user_info', username=current_user.name))

	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template("edit_userinfo.html", form=form)


@auth.route('/user/adminedit', methods=['GET', 'POST'])
@login_required
@admin_required
def adminedit():
	form = AdminEditForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.confirmed = form.confirmed.data
		current_user.phone_number = form.phone_number.data
		current_user.age = form.age.data
		current_user.email = form.email.data
		current_user.role = Role.query.filter_by(role=form.role.data)

		db.session.add(current_user._get_current_object())
		db.session.commit()
		return redirect(url_for('auth.user_info'))

	form.name.data = current_user.name
	form.location.data = current_user.location
	form.confirmed.data = current_user.confirmed
	form.phone_number.data = current_user.phone_number
	form.age.data = current_user.age
	form.email.data = current_user.email
	form.role = current_user.role
	
	return render_template("edit_userinfo.html", form=form)
	
	




		
		

	

