from flask import Flask
from flask_restful import Api
from db import BackendDB, UsersDB
from resource import DbAPI, TableAPI, RegisterAPI

app = Flask(__name__)
api = Api(app)

api.add_resource(DbAPI, '/<string:db_name>')
api.add_resource(TableAPI, '/<string:db>/<string:table>')
api.add_resource(RegisterAPI, '/register')

if __name__ == '__main__':
    app.run(debug=True)
