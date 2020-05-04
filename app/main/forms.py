from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField

class PostForm(FlaskForm):
	subject = StringField("suject", validators=[DataRequired()])
	content = PageDownField('content', validators=[DataRequired()])
	submit = SubmitField('Submit')

class CommentForm(FlaskForm):
	content = PageDownField('Type Your Comment:', validators=[DataRequired()])
	submit = SubmitField('Submit')
