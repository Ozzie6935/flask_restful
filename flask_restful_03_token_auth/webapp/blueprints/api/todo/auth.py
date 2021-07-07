from flask_restful import reqparse, abort, Resource
from webapp.extensions import db
from webapp.blueprints.api.todo.tables import User
from flask_httpauth import HTTPBasicAuth
from flask import g


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.authenticated(password=password):
        return False

    g.user = User.get_user_by_username(username=username)
    return True

class UserInit(Resource):
    def post(self):
        from webapp.util_uuid import UUIDOPS
        import secrets
        d = [ {
            'username': 'ozzie',
            'password': "abc123",
            'account_number': UUIDOPS.getNewUUIDhex(length=12),
            'api_key': secrets.token_hex(12),
            'admin': True,
            },
            {
            'username': 'mark',
            'password': "abc123",
            'account_number': UUIDOPS.getNewUUIDhex(length=12),
            'api_key': secrets.token_hex(12),
            'admin': False,
            }
        ]
        for i in d:
            r = User(**i)
            db.session.add(r)
            db.session.commit()

        return {'result': 'success'}, 201


class UserAuth(Resource):
    @auth.login_required
    def get(self):
        # --header "X-Vault-Token: $VAULT_TOKEN" \
        return g.user
        return {'result': 'success'}
