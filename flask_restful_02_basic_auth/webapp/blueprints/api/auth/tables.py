from webapp.extensions import db
from webapp.util_sqlalchemy import SQLALCHEMYOPS
from webapp.util_uuid import UUIDOPS
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import abort
import secrets
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), index=True)
    password = db.Column(db.String(128), nullable=False, server_default='')
    # account_number = db.Column('account_number', db.String(12), default='', unique=True)
    # api_key = db.Column('api_key', db.String(24), default='', unique=True)
    admin = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = User.encrypt_password(kwargs.get('password', ''))
        # self.account_number = UUIDOPS.getNewUUIDhex(length=12)
        # self.api_key = secrets.token_hex(12)

    @classmethod
    def get_user_by_username(cls, username=''):
        d = User.query.filter_by(username = username).first()
        if d:
            return SQLALCHEMYOPS.to_jsonify(res=d)


    @classmethod
    def encrypt_password(cls, plaintext_password):

        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    def authenticated(self, with_password=True, password=''):

        if with_password:
            return check_password_hash(self.password, password)

        return True

    @classmethod
    def add_user_to_db(cls, d):
        d['admin'] = cls.to_bool(d['admin'])
        r = User(**d)
        db.session.add(r)
        db.session.commit()

        return cls.get_user_by_username(username=d['username'])

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
