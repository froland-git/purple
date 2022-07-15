from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # for web-signature JSON
from flask import current_app


# ----- [09a] Permission bitmask class -----
# https://pythonpip.ru/osnovy/staticheskie-peremennye-i-metody-v-python
# To check:
#   >>>  ./manage.py shell
#   >>> Permission().COMMENT
#   2
#   >>> Permission().ADMINISTER
#   128
class Permission:
    FOLLOW = 0x01                # 0b00000001
    COMMENT = 0x02               # 0b00000010
    WRITE_ARTICLES = 0x04        # 0b00000100
    MODERATE_COMMENTS = 0x08     # 0b00001000
    ADMINISTER = 0x80            # 0b10000000


# DB Relationship:
#    ONE role to MANY users
#    https://dev-gang.ru/doc/flask-sqlalchemy/models/

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # [09a] Since the index takes up space, only those fields that are being selected need to be indexed
    permissions = db.Column(db.Integer)  # [09a]
    users = db.relationship('User', backref='role', lazy='dynamic')  # 'role' will be a new option for 'User' class

    # ----- [09a] Staticmethod to add role to DB -----
    # Anonymous     = 0b00000000 (0x00) - this role is out of DB
    # User          = 0b00000001 | 0b00000010 | 0b00000100 = 0b00000111 (0x07)
    # Moderator     = 0b00000001 | 0b00000010 | 0b00000100 | 0b00001000 = 0b00001111 (0x0f)
    # Administrator = 0b11111111 (0xff)
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |  # It is a bitwise OR of integers, i.e. 00001111 | 10000000 = 10001111
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:  # r - key for dictionary 'roles'
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]  # Permission.FOLLOW & Permission.COMMENT ...
            role.default = roles[r][1]  # True or False
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128)) # This is like __init__ in ordinary class
    confirmed = db.Column(db.Boolean, default=False)

    # ----- [09a] Set role 'Administrator' or 'Default' role  -----
    def __init__(self, **kwargs):
        # Class 'User' is a child of 'UserMixin' and 'db.Model'
        # https://tirinox.ru/super-python/
        super(User, self).__init__(**kwargs)  # same as super().__init__(x)
        # We can use self.role due to users = db.relationship('User', backref='role', lazy='dynamic')
        # in class 'Role'
        # https://flask-sqlalchemy-russian.readthedocs.io/ru/latest/models.html
        if self.role is None:
            if self.email == current_app.config['PURPLE_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # Doc: https://www.tutorialsteacher.com/python/property-decorator
    @property
    def password(self): # This is like a getter
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Generate marker
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # Method dumps() generates digital signature and create marker
        return s.dumps({'confirm': self.id}) # 'confirm' default key, self.id - value

    # Check marker and save it in confirmed
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Method loads() decrypts marker
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self) # db.session.add() for prepare, db.session.commit() for for the record
        return True

    # ----- [08g] Method to generate token to reset password -----
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    # ----- [08g] Method to reset password -----
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))  # {'reset': self.id}
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # ----- [08e] Method to generate token to change email address -----
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')  # Hash will include two parameters

    # ----- [08e] Method to change email address -----
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)  # commit() in the view.py
        return True

    # ----- [09a] Methods to check permissions for logged in users -----
    # 'self.role.permissions' is additional property 'role' in class 'User'
    # to show all roles connected with this user (role_id is Foreign Key)
    #
    # 'permissions' is property in class 'Role'
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)  # Invoke method can

    def __repr__(self):
        return '<User %r>' % self.username


# ----- [09a] Separate class for Anonymous Users -----
# No need to check login status for that users
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
