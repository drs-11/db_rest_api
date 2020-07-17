import os
import sqlite3
import datetime
import jwt
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy import create_engine

class BackendDB:

    def __init__(self, file="CONFIG"):
        self.config_dict = self.load_config_file(file)
        self.engine = create_engine(self.config_dict['ENGINE_PATH_WIN_AUTH'])

    @staticmethod
    def load_config_file(file):
        config_dict = dict()

        if not os.path.isfile("./CONFIG"):
            #enter default config details here
            config_dict = {                               \
                            'DIALECT' : 'oracle',         \
                            'SQL_DRIVER' : 'cx_oracle',   \
                            'USERNAME' : 'hr',            \
                            'PASSWORD' : 'apple',         \
                            'HOST' : 'localhost',         \
                            'PORT' : 51521,               \
                            'SERVICE' : 'XEPDB1'          \
                          }


        else:
            with open(file, 'r') as config_file:
                for line in config_file.readlines():
                    parameter, value = map(str.split, line.split("="))
                    value = value.strip("'")
                    config_dict[parameter] = value

        config_dict['ENGINE_PATH_WIN_AUTH'] =                                \
                                    config_dict['DIALECT'] + '+' +           \
                                    config_dict['SQL_DRIVER'] + '://' +      \
                                    config_dict['USERNAME'] + ':' +          \
                                    config_dict['PASSWORD'] +'@' +           \
                                    config_dict['HOST']                      \
                                    + ':' + str(config_dict['PORT']) +       \
                                    '/?service_name='                        \
                                    + config_dict['SERVICE']

        return config_dict

class UsersDB:

    def __init__(self, db_path=os.getcwd()):
        self.con = sqlite3.connect(os.path.join(db_path, 'users.db'), check_same_thread=False)
        self.cur = self.con.cursor()
        self.SECRET_KEY = self.get_secret_key()
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
        query = "INSERT INTO users (email, passwd) VALUES (?, ?)"
        self.cur.execute(query, (email, passwd_hash))
        self.con.commit()

    def check_if_user_exists(self, email):
        query = "SELECT id FROM users WHERE email=?"
        result = self.cur.execute(query, (email, )).fetchone()
        return result

    def get_passwd_hash(self, id):
        query = "SELECT passwd FROM users WHERE id=?"
        passwd = self.cur.execute(query, (id, )).fetchone()[0]
        return passwd

    def verify_request(self, req_data):
        user_id = self.decode_auth_token(req_data.get('auth-token'))
        passwd = self.get_passwd_hash(id=user_id)
        if check_password_hash(
            passwd, req_data.get('password')
        ):
            return True
        else:
            return False
    def encode_auth_token(self, email):
        query = "SELECT id FROM users WHERE email =?"
        user_id = self.cur.execute(query, (email, )).fetchone()[0]
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

    def get_secret_key(self):
        '''
        secret_key = os.getenv('SECRET_KEY')
        if secret_key is None:
            secret_key = os.urandom(24)
            os.environ['SECRET_KEY'] = str(secret_key)
        return (secret_key)
        '''
        if os.path.exists('./SECRET_KEY'):
            with open('./SECRET_KEY', 'rb') as secret_file:
                secret_key = secret_file.read()
        else:
            secret_key = os.urandom(24)
            with open('./SECRET_KEY', 'wb') as secret_file:
                secret_file.write(secret_key)
        return secret_key
    def __exit__(self, ext_type, exec_value, traceback):
        self.cursor.close()
        if isinstance(exec_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

