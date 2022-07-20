import unittest
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission
import time
from datetime import datetime


class UserModelTestCase(unittest.TestCase):
    # Basic method performed before all test_<name> methods
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()  # [09a] insert roles to data-test.sqlite

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

    # ----- [08e] Use invalid confirmation token for existing user -----
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

    # ----- [08g] Test how we can reset token (true) -----
    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    # ----- [08g] Test how we can reset token (false) -----
    def test_invalid_reset_token(self):
        u = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(u.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    # ----- [08g] Test how we can change email address (valid) -----
    def test_valid_email_change_token(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    # ----- [08g] Test how we can change email address (invalid) -----
    def test_invalid_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    # ----- [08g] Test how we can change email address (duplicate) -----
    def test_duplicate_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    # ----- [09a] Test to check permission -----
    def test_roles_and_permissions(self):
        u = User(email='john@example.com', password='cat')
        # Permission 'WRITE_ARTICLES' is a part of default role 'User'
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    # ----- [09a] Test to check permission for anonymous_user -----
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    # ----- [10a] Test to check member_since field -----
    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    # ----- [10a] Test to check last_seen field -----
    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)
