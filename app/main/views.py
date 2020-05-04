from . import main
from .forms import PostForm, CommentForm
from flask import render_template, redirect, url_for, request, request, make_response
from flask_login import current_user, login_required
from ..models import Permissions, Post, User, Comment
from .. import db
from flask import current_app
from ..decorators import permission_required

@main.route("/", methods=['GET','POST'])
def index():
	form = PostForm()
	if form.validate_on_submit() and current_user.has_perm(Permissions.WRITE):
		post = Post()
		post.subject = form.subject.data
		post.content = form.content.data

		db.session.add(post)
		db.session.commit()

		return redirect(url_for(".index"))
	
	show_fellowed = bool(request.cookies.get('show_fellowed', ''))

	if show_fellowed and not current_user.is_anonymous:
		query = current_user.fellowed_postquery
	else:
		query = Post.query

	write_perm = Permissions.WRITE
	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.post_time.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
	posts = pagination.items
	
	#练习cookie用法：
	resp=make_response(render_template("index.html", form=form, posts=posts, write_perm=write_perm, pagination=pagination))	
	resp.set_cookie('mycookie', 'hello', max_age=3600)	
	return resp

@main.route("/user/<int:id>", methods=['GET', 'POST'])
@login_required
def post(id):
	form = CommentForm()
	post = Post.query.filter_by(id=id).first()

	if form.validate_on_submit():
		comment = Comment(author_id=current_user.id, post_id=id ,content=form.content.data)
		db.session.add(comment)
		db.session.commit()
		return redirect(url_for('.post', id=post.id))

	comments = post.comments.all()
	return render_template('post.html', comments=comments, post=post, form=form)

@main.route("/user/edit_post/<int:id>")
@login_required
def edit_post(id):
	form = PostForm()
	post = Post.query.filter_by(id=id).first()

	if post and form.validate_on_submit():
		if current_user==post.author or current_user.has_perm(Permissions.WRITE):
			post.content = form.content.data
			db.session.add(post)
			db.session.commit()
			return redirect(url_for("auth.user_info", username=post.author.name))
	
	form.content.data = post.content
	return render_template('edit_post.html', user=current_user, form=form)

@main.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(name=username).first()
	if user:
		current_user.fellow(user)
	return redirect(url_for('auth.user_info', username=username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(name=username).first()
	if user:
		current_user.unfellow(user)
	return redirect(url_for('auth.user_info', username=username))
	
@main.route('/fellowed_list/<username>')
@login_required
def fellowed_list(username):
	user = User.query.filter_by(name=username).first()
	if user:
		fellowed = user.fellowed.all()
		return render_template('fellowed_list.html', fellowed=fellowed, user=user)
	return redirect(url_for('auth.user_info'))

@main.route('/fellower_list/<username>')
@login_required
def fellower_list(username):
	user = User.query.filter_by(name=username).first()
	if user:
		fellower = user.fellower.all()
		return render_template('fellower_list.html', fellower=fellower, user=user)
	return redirect(url_for('auth.user_info'))

@main.route("/all")
def all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_fellowed', '', max_age=30*24*60*60)
	return resp

@main.route("/show_fellowed")
@login_required
def show_fellowed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_fellowed', '1', max_age=30*24*60*60)
	return resp


@main.route("/moderate")
@login_required
@permission_required(Permissions.ADMIN)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.comment_time.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
	comments = pagination.items
	
	return render_template('moderate.html', comments=comments, pagination=pagination, page=page)

@main.route("/comment_enable/<int:id>")
@login_required
@permission_required(Permissions.ADMIN)
def comment_enable(id):
	comment = Comment.query.filter_by(id=id).first()
	if comment:
		comment.disable = False
		db.session.add(comment)
		db.session.commit()
	return redirect(url_for('.moderate',page=request.args.get('page',1, type=int)))

@main.route("/comment_disable/<int:id>")
@login_required
@permission_required(Permissions.ADMIN)
def comment_disable(id):
	comment = Comment.query.filter_by(id=id).first()
	if comment:
		comment.disable = True
		db.session.add(comment)
		db.session.commit()
	return redirect(url_for('.moderate',page=request.args.get('page',1, type=int)))





