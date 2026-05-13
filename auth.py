from functools import wraps
from flask import session, abort


def login_required(f):
    """Require the caller to be logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            abort(401)
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Require the caller to be an admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            abort(401)
        if session.get("user_role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


def current_user_id():
    return session.get("user_id")