import sqlite3
import os
import datetime
import jwt
#from db_api import bcrypt_app
from flask_bcrypt import check_password_hash, generate_password_hash

class UsersDB:

    def __init__(self, db_path=os.getcwd()):
        self.con = sqlite3.connect(os.path.join(db_path, 'users.db'), check_same_thread=False)
        self.cur = self.con.cursor()
        self.SECRET_KEY = 'apple'
        self.init_table()

    def init_table(self):
        user_sql = """
                   CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   email TEXT NOT NULL,
                   passwd TEXT NOT NULL)
                   """
        self.cur.execute(user_sql)

    def add_user(self, email, passwd):
        passwd_hash = generate_password_hash(passwd).decode()
        add_sql = "INSERT INTO users (email, passwd) VALUES (?, ?)"
        self.cur.execute(add_sql, (email, passwd_hash))
        self.con.commit()

    def check_if_user_exists(self, email):
        result = self.cur.execute("SELECT id FROM users WHERE email='{}'".format(email)).fetchone()
        return result

    def get_passwd_hash(self, id):
        passwd = self.cur.execute("SELECT passwd FROM users WHERE id={}".format(id)).fetchone()[0]
        return passwd

    def verify_request(self, req_data):
        print(req_data)
        user_id = self.decode_auth_token(req_data.get('auth-token'))
        passwd = self.get_passwd_hash(id=user_id)
        if check_password_hash(
            passwd, req_data.get('password')
        ):
            return True
        else:
            return False
    def encode_auth_token(self, email):
        user_id = self.cur.execute("SELECT id FROM users WHERE email = '{}'".format(email)).fetchone()[0]
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=8),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                self.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def decode_auth_token(self, auth_token):
        try:
            payload = jwt.decode(auth_token, self.SECRET_KEY)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Register again.'
        except jwt.InvalidTokenError:
            return 'Invalid token.'

    def __exit__(self, ext_type, exec_value, traceback):
        self.cursor.close()
        if isinstance(exec_value, Exception):
            self.connection.rollback()
        else:
            self.connection.close()
        self.connection.close()




