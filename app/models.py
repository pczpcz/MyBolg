from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
import hashlib
from markdown import markdown
import bleach

class Permissions:
	FOLLOW = 1
	COMMENT = 2
	WRITE = 4
	MODERATE = 8
	ADMIN = 16

class Fellow(db.Model):
	__tablename__ = 'follows'

	fellower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	fellowed_id = db.Column(db.Integer,db.ForeignKey('users.id'), primary_key=True)

class User(db.Model, UserMixin):
	__tablename__='users'
	
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String)
	age = db.Column(db.Integer)
	phone_number = db.Column(db.String)
	location = db.Column(db.String)
	email = db.Column(db.String)
	about_me = db.Column(db.Text())

	md5_hash = db.Column(db.String())

	account_createtime = db.Column(db.DateTime(), default=datetime.utcnow)
	login_lasttime = db.Column(db.DateTime(), default=datetime.utcnow)
		
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comments =db.relationship('Comment', backref='author', lazy='dynamic')
	
	fellowed = db.relationship('Fellow', foreign_keys=[Fellow.fellower_id],
			backref=db.backref('fellower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	fellower = db.relationship('Fellow', foreign_keys=[Fellow.fellowed_id], 
			backref=db.backref('fellowed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role == None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(name='Admin').first()
			if self.role == None:
				self.role = Role.query.filter_by(default=True).first()

	@property
	def password():
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	@property
	def fellowed_postquery(self):
		return Post.query.join(Fellow, Fellow.fellowed_id==Post.author_id).filter(Fellow.fellower_id==self.id)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def get_id(self):
		return self.id

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id}).decode('utf-8')

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data['confirm'] != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def has_perm(self, perm):
		return self.role and self.role.has_permission(perm)

	def is_adminstrator(self):
		return self.has_perm(Permissions.ADMIN)

	def update_logintime(self):
		login_lasttime = datetime.utcnow()
		db.session.add(self)
		db.session.commit()

	def get_md5hash(self):
		return hashlib.md5(self.email.encode('utf-8')).hexdigest()

	def gravatar(self, size=100, default='identicon', rating='g'): 
		url = 'https://secure.gravatar.com/avatar/'
		img_hash = self.md5_hash or self.get_md5hash()
		return '{url}/{img_hash}?s={size}&r={rating}&d={default}'.format(url=url, img_hash=img_hash, size=size, rating=rating, default=default)

	def fellow(self, user):
		fellow = Fellow(fellower=self, fellowed=user)
		db.session.add(fellow)
		db.session.commit()

	def unfellow(self, user):
		fellow = self.fellowed.filter_by(fellowed_id=user.id).first()
		db.session.delete(fellow)
		db.session.commit()

	def isfellowing(self, user):
		return self.fellowed.filter_by(fellowed_id=user.id).first() is not None

	def isfellowed_by(self, user):
		return self.fellower.filter_by(fellower_id=user.id).first() is not None

class AnonymousUser(AnonymousUserMixin):
	def has_perm(self, perm):
		return False
	def is_adminstrator(self):
		return False

login_manager.anonymous_user = AnonymousUser

class Role(db.Model):
	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)

	users = db.relationship('User', backref='role', lazy='dynamic')

	def __init__(self, **kwargs):
		super(Role, self).__init__(**kwargs)
		if self.permissions == None:
			permissions = 0

	def set_permission(self, perm):
		self.permissions = perm

	def has_permission(self, perm):
		return self.permissions & perm == perm

	def remove_permission(self, perm):
		if self.has_permission(perm):
			self.permission -= perm

	def add_permission(self, perm):
		if not self.has_permission(perm):	
			self.permissions += perm

	def reset_permission(self):
		self.permissions = 0

	@staticmethod
	def insert_roles():
		roles = {'User':[Permissions.FOLLOW, Permissions.COMMENT, Permissions.WRITE],
			'Moderator':[Permissions.FOLLOW, Permissions.COMMENT, Permissions.WRITE, Permissions.MODERATE],
			'Admin':[Permissions.FOLLOW, Permissions.COMMENT, Permissions.WRITE, Permissions.MODERATE, Permissions.ADMIN]
		}
		
		default_role = 'User'
		for rname in roles:
			role = Role.query.filter_by(name=rname).first()
			if role is None:
				role = Role(name=rname)
			role.reset_permission()
			for perm in roles[rname]:
				role.add_permission(perm)

			role.default = (role.name == default_role)
			db.session.add(role)

		db.session.commit()

class Post(db.Model):
	__tablename__ = 'posts'

	id = db.Column(db.Integer, primary_key=True)
	subject = db.Column(db.String())
	content = db.Column(db.Text())
	content_html = db.Column(db.Text())
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
	post_time = db.Column(db.DateTime(), index=True, default=datetime.utcnow)

	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 
				'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']

		target.content_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))
		target.author = current_user._get_current_object()

db.event.listen(Post.content, 'set', Post.on_changed_body)

class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, primary_key=True)
	subject = db.Column(db.String())
	content = db.Column(db.Text())
	content_html = db.Column(db.Text())
	comment_time = db.Column(db.DateTime(), index=True, default=datetime.utcnow)

	author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)

	disable = db.Column(db.Boolean, default=False)

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 
				'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']

		target.content_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))
		target.author = current_user._get_current_object()

db.event.listen(Comment.content, 'set', Comment.on_changed_body)



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
