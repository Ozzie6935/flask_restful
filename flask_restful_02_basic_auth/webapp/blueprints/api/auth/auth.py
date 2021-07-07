from flask_restful import reqparse, abort, Resource
from webapp.extensions import db
from webapp.blueprints.api.auth.tables import User
from flask_httpauth import HTTPBasicAuth
from flask import g, request
from functools import wraps


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.authenticated(password=password):
        abort(401)

    g.user = User.get_user_by_username(username=username)
    return True


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #user = User.get_user_by_username(username=username)
            #if user[permission] == True:
            if g.user[0]['admin'] == False:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def abort_if_not_args(args=None):
    if not args:
        abort(404, message="missing arguments dict")
    if not 'username' in args or not 'password' in args:
        abort(404, message="username and password are requried fields")
    return True


auth_parser = reqparse.RequestParser(bundle_errors=True)
auth_parser.add_argument('username', required=True, help="username is requrired field", case_sensitive=True)
auth_parser.add_argument('password', required=True, help="password is requrired field", case_sensitive=True)
auth_parser.add_argument('admin', required=False, help='Bad choice: {error_msg}', case_sensitive=False, choices=('True', 'False'), default='False')


class UserInit(Resource):
    def post(self):
        args = auth_parser.parse_args()
        abort_if_not_args(args)
        result = User.add_user_to_db(d=args)
        return result, 201


class UserAuth(Resource):
    @auth.login_required()
    def get(self):

        return g.user


class AdminAuth(Resource):
    @auth.login_required()
    @permission_required('admin')
    def put(self, user):
        args = auth_parser.parse_args()
        abort_if_not_args(args)
        result = User.update_user(user=user, d=args)
        return result, 201
