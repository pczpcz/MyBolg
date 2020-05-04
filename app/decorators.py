from flask_login import current_user
from functools import wraps
from flask import abort
from .models import Permissions


def permission_required(perm):
	def decorator(f):
		@wraps(f)
		def function_decorator(*args, **kwargs):
			if not current_user.has_perm(perm):
				abort(403)
			return f(*args, **kwargs)
		return function_decorator
	return decorator

def admin_required(f):
	return permission_required(Permissions.ADMIN)(f)
