from random import randint
from faker import Faker
from . import db
from .models import User, Post
from sqlalchemy.exc import IntegrityError	

def create_fakeusers(count=100):
	fake = Faker()
	i = 0
	while(i<count):
		user = User(name=fake.name(),
				email=fake.email(),
				password='123456', 
				confirmed=True, 
				about_me=fake.text(), 
				location=fake.city(), 
				account_createtime=fake.past_date())
		db.session.add(user)
		try:
			db.session.commit()
			i += 1
		except IntegrityError:	
			db.session.rollback()

def create_fakeposts(count=100):
	fake = Faker()
	user_count = User.query.count()

	for i in range(count):
		u = User.query.offset(randint(0, user_count-1)).first()
		p = Post(content=fake.text(), post_time=fake.past_date(), author=u)		
		db.session.add(p)
	db.session.commit()
