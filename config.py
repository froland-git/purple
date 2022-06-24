import os.path

basedir = os.path.abspath(os.path.dirname(__file__)) # SQLite - sqlite:///absolute/path/to/database

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '8025'))
    # MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
    #     ['true', 'on', '1']
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    PURPLE_MAIL_SUBJECT_PREFIX = '[Purple]'
    PURPLE_MAIL_SENDER = 'Purple Admin <purple@example.com>'
    PURPLE_ADMIN = os.environ.get('PURPLE_ADMIN')

    # static method is easier to import than regular functions because each function does not need to be separately imported
    # Myclass.staticmethod()
    # or
    # my_obj = Myclass()
    # my_obj.staticmethod()
    @staticmethod
    def init_app(app):
        pass # this is plug


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-prod.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
