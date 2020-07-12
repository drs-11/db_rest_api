import os
from sqlalchemy.engine import create_engine

class InitDB:

    def __init__(self):
        self.config_dict = self.load_config_file()
        self.engine = create_engine(self.config_dict['ENGINE_PATH_WIN_AUTH'])

    def connect_db(self):
        pass

    @staticmethod
    def load_config_file(file="CONFIG"):
        config_dict = dict()

        if not os.path.isfile("./CONFIG"):
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

