import json
import os
import sqlite3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from db import InitDB


app = Flask(__name__)
api = Api(app)
backend_db = InitDB()

class DB(Resource):
    def get(self, db_name):
        with backend_db.engine.connect() as connection:
            output = connection.execute("SELECT {} FROM user_tables".format('table_name'))
        return json.dumps([dict(row.items()) for row in output])

class Table(Resource):
    def get(self, db, table):
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
                output = connection.execute("SELECT {} FROM {} WHERE ROWNUM <= {}".format(col_name, table, limit))
            else:
                output = connection.execute("SELECT {} FROM {} WHERE ROWNUM <= {}"   \
                                            " ORDER BY {} {}".format(col_name, \
                                            table, limit, order_by,     \
                                            direction))
        return json.dumps([dict(row.items()) for row in output])

    def normalize_query_param(self, value):
       return value if len(value) > 1 else value[0]


    def normalize_query(self, params):
       params_non_flat = params.to_dict(flat=False)
        return {k: self.normalize_query_param(v) for k, v in params_non_flat.items()}

    def return_error(self, error_no):
        pass

api.add_resource(DB, '/<string:db_name>')
api.add_resource(Table, '/<string:db>/<string:table>')

if __name__ == '__main__':
    app.run(debug=True)
