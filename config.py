import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = 'jdlfd jdklf dlla ld2oq n'
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'myweb Admin <1099311614@qq.com>'
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	FLASKY_POSTS_PER_PAGE = 10

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

class TestingConfig(Config):
	pass

class ProductionConfig(Config):
	pass

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,

	'default': DevelopmentConfig
}





