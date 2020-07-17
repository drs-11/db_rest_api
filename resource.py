import os
import json
from flask import request, jsonify
from flask_restful import Resource
from db import BackendDB, UsersDB

backend_db = BackendDB()
users_db = UsersDB()

class RegisterAPI(Resource):
    def post(self):
        post_data = request.get_json()
        if post_data is None:
            response = {
                "status" : 'fail',
                'message' : 'Please enter email and password.'
            }
            return response, 401
        user = users_db.check_if_user_exists(email=post_data.get('email'))
        if not user:
            users_db.add_user(email=post_data.get('email'),
                              passwd=post_data.get('password'))
            auth_token = users_db.encode_auth_token(post_data.get('email'))
            response = {
                'status' : 'success',
                'message' : 'Successfully registered.',
                'auth-token' : auth_token.decode()
            }
            return response, 201
        else:
            response = {
                'status' : 'fail',
                'message' : 'User already exists!'
            }
            return response, 401

class DbAPI(Resource):
    def get(self, db_name):
        req_data = request.get_json()
        if req_data is None:
            response = {
                'status' : 'fail',
                'message' : 'Please provide authentication details.'
            }
            return response, 401
        authentic = users_db.verify_request(req_data)
        if authentic:
            if db_name != backend_db.config_dict['SERVICE']:
                response = {
                    'status' : 'fail',
                    'message' : 'Please provide the correct database name.'
                }
            else:
                with backend_db.engine.connect() as connection:
                    output = connection.execute("SELECT table_name FROM user_tables")
                return json.dumps([dict(row.items()) for row in output])
        else:
            response = {
                'status' : 'fail',
                'message' : 'Provide a valid auth token.'
            }
            return response, 401

class TableAPI(Resource):
    def get(self, db, table):
        req_data = request.get_json()
        authentic = users_db.verify_request(req_data)
        if authentic:
            return self.process_request(db, table), 200
        else:
            response = {
                'status' : 'fail',
                'message' : 'Provide a valid auth token.'
            }
            return response, 401

    def process_request(self, db, table):
        query = self.normalize_query(request.args)
        col_name = query.get('col')
        order_by = query.get('order_by')
        limit = query.get('limit')
        direction = query.get('direction')

        if col_name is None: col_name = '*'
        elif type(col_name) is list: col_name = ",".join(col_name)
        if limit is None: limit = '100'
        if direction is None: direction = 'ASC'

        with backend_db.engine.connect() as connection:
            if order_by is None:
                output = connection.execute(f"SELECT {col_name} FROM {table} WHERE ROWNUM <= {limit}")
            else:
                output = connection.execute(f"SELECT {col_name} FROM {table} "
                                            f"WHERE ROWNUM <= {limit} "
                                            f"ORDER BY {order_by} {direction}")

        return json.dumps([dict(row.items()) for row in output])

    def normalize_query_param(self, value):
        return value if len(value) > 1 else value[0]


    def normalize_query(self, params):
        params_non_flat = params.to_dict(flat=False)
        return {k: self.normalize_query_param(v) for k, v in params_non_flat.items()}
