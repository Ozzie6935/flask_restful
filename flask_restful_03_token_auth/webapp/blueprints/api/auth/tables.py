from webapp.extensions import db
from webapp.util_sqlalchemy import SQLALCHEMYOPS
from webapp.util_uuid import UUIDOPS
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import abort
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired)
from flask import current_app, session, request
import jwt
import time


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), index=True, unique=True, nullable=True)
    password = db.Column(db.String(128), nullable=True, server_default='')
    client_id = db.Column('client_id', db.String(12), unique=True, nullable=True)
    client_secret = db.Column('client_secret', db.String(24), unique=True, nullable=True)
    admin = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = User.encrypt_password(kwargs.get('password', ''))
        # self.client_id = UUIDOPS.getNewUUIDhex(length=12)
        # self.client_secret = secrets.token_hex(12)


    @classmethod
    def serialize_token(cls, grant_type='user_credentials', expiration=3600, username_or_client_id=''):

        private_key = current_app.config['SECRET_KEY']
        serializer = Serializer(private_key, expires_in = expiration)

        if grant_type == 'client_credentials':
            token = serializer.dumps({'client_id': username_or_client_id, 'grant_type': 'client_credentials'}).decode('utf-8')
        else:
            token = serializer.dumps({'username': username_or_client_id, 'grant_type': 'user_credentials'}).decode('utf-8')

        d = {"access_token": token, "expires_in": serializer.expires_in}

        return d

    @classmethod
    def deserialize_token(cls, token):

        private_key = current_app.config['SECRET_KEY']
        deserializer = Serializer(private_key)

        try:
            decoded_payload = deserializer.loads(token)
            if decoded_payload['grant_type'] == 'client_credentials':
                r = cls.get_user_by_client_id(client_id=decoded_payload['client_id'])
            elif decoded_payload['grant_type'] == 'user_credentials':
                r = cls.get_user_by_username(username=decoded_payload['username'])
            else:
                return [{'Status': 'Failed', 'Message': str(e)}]

            r[0]['Status'] = "Success"
            return r
        except SignatureExpired as e:
            return [{'Status': 'Failed', 'Message': str(e)}] # valid token, but expired
        except BadSignature as e:
            return [{'Status': 'Failed', 'Message': str(e)}] # invalid token
        except Exception as e:
            return [{'Status': 'Failed', 'Message': str(e)}] # other excepitons
        return [{'Status': 'Failed', 'Message': str(e)}]



    @classmethod
    def get_user_by_username(cls, username=''):
        d = User.query.filter_by(username = username).first()
        if d:
            result = SQLALCHEMYOPS.to_jsonify(res=d)

            return result
        return None

    @classmethod
    def get_user_by_client_id(cls, client_id=''):
        d = User.query.filter_by(client_id = client_id).first()
        if d:
            result = SQLALCHEMYOPS.to_jsonify(res=d)

            return result
        return None

    @classmethod
    def encrypt_password(cls, plaintext_password):

        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    def authenticated(self, with_password=True, password=''):

        if with_password:
            return check_password_hash(self.password, password)

        return True

    def client_authenticated(self, with_password=True, client_secret=''):

        if with_password:
            return check_password_hash(self.client_secret, client_secret)

        return True

    @classmethod
    def add_user_to_db(cls, d):
        d['admin'] = cls.to_bool(d['admin'])
        r = User(**d)
        db.session.add(r)
        db.session.commit()

        return cls.get_user_by_username(username=d['username'])

    @classmethod
    def add_client_to_db(cls, d):
        d['admin'] = cls.to_bool(d['admin'])
        client_secret = secrets.token_hex(12)
        d['client_secret'] = cls.encrypt_password(plaintext_password=client_secret)
        r = User(**d)
        db.session.add(r)
        db.session.commit()

        r = cls.get_user_by_client_id(client_id=d['client_id'])
        r[0]['client_secret'] = client_secret

        return r

    @classmethod
    def update_user(cls, user='', d={}):
        d['admin'] = cls.to_bool(d['admin'])
        d['password'] = cls.encrypt_password(d['password'])

        u = User.query.filter(User.username == user).first()
        #setattr(u, **d)
        if u:
            for key, value in d.items():
                setattr(u, key, value)
            # u.username = d['username']
            # u.password = cls.encrypt_password(d['password'])
            # u.admin =  cls.to_bool(d['admin'])

            db.session.add(u)
            db.session.commit()

        return cls.get_user_by_username(username=d['username'])

    @classmethod
    def to_bool(cls, s):
        if isinstance(s, str):
            if s.lower() == 'true':
                 return True
            elif s.lower() == 'false':
                 return False
            else:
                 raise ValueError # evil ValueError that doesn't tell you what the wrong value was
        elif isinstance(s, bool):
            return bool(s)
        elif s == 1:
            return True
        elif s == 0:
            return False
        else:
             raise ValueError
