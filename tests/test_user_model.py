import unittest
from app import create_app, db
from app.models import User
import time


class UserModelTestCase(unittest.TestCase):
    # Basic method performed before all test_<name> methods
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # Basic method performed after all test_<name> methods
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    # ----- [08e] Generate and check confirm token -----
    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u) # prepare to add
        db.session.commit() # app data to db
        token = u.generate_confirmation_token() # Generate marker
        self.assertTrue(u.confirm(token)) # Check marker and save it in confirmed field in Model

    # ----- [08e] Use invalid configmation token for existing user -----
    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token)) # False if we use wrong token for user

    # ----- [08e] Check expiration -----
    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1) # expiration = 1 sec
        time.sleep(2)
        self.assertFalse(u.confirm(token))