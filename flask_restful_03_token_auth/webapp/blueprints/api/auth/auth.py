from flask_restful import reqparse, abort, Resource
from webapp.extensions import db
from webapp.blueprints.api.auth.tables import User
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import g, request, jsonify
from functools import wraps
from werkzeug.http import HTTP_STATUS_CODES


auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

@auth.verify_password
def verify_password(username_or_client_id, password_or_client_secret):

    # try to authenticate with client_id/client_secret
    user = User.query.filter_by(client_id = username_or_client_id).first()
    if user and user.client_authenticated(client_secret=password_or_client_secret):
        g.user = User.get_user_by_client_id(client_id=username_or_client_id)
        return True
    else:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_client_id).first()
        if user and user.authenticated(password=password_or_client_secret):
            g.user = User.get_user_by_username(username=username_or_client_id)
            return True
        else:
            abort(401)


@token_auth.verify_token
def verify_token(token):
    user = User.deserialize_token(token=token)
    if user[0]['Status'] == "Success":
        g.user = user
        return True

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user[0]['admin'] == False:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def abort_if_not_args(args=None):
    if not args:
        abort(404, message="missing arguments dict")
    return True

auth_parser = reqparse.RequestParser(bundle_errors=True)
auth_parser.add_argument('username', required=True, help="username is required field", case_sensitive=True)
auth_parser.add_argument('password', required=True, help="password is required field", case_sensitive=True)
auth_parser.add_argument('admin', required=False, help='Bad choice: {error_msg}', case_sensitive=False, choices=('True', 'False'), default='False')


client_parser = reqparse.RequestParser(bundle_errors=True)
client_parser.add_argument('client_id', required=True, help="Client ID is a required field", case_sensitive=True)
client_parser.add_argument('admin', required=False, help='Bad choice: {error_msg}', case_sensitive=False, choices=('True', 'False'), default='False')


token_parser = reqparse.RequestParser(bundle_errors=True)
token_parser.add_argument('grant_type', required=True, help="Grant Type is required field", case_sensitive=False, choices=('user_credentials', 'client_credentials'), default='user_credentials')


class ClientInit(Resource):
    def post(self):
        args = client_parser.parse_args()
        abort_if_not_args(args)
        result = User.add_client_to_db(d=args)
        return result, 201

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

class UserAuthToken(Resource):
    @token_auth.login_required
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

class AuthToken(Resource):
    @auth.login_required()
    def post(self):
        args = token_parser.parse_args()
        abort_if_not_args(args)

        if args['grant_type'] == 'client_credentials':
            token = User.serialize_token(grant_type=args['grant_type'], username_or_client_id=g.user[0]['client_id'])
        else:
            token = User.serialize_token(grant_type=args['grant_type'], username_or_client_id=g.user[0]['username'])

        return token, 201
