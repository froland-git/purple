# purple

## List of important packages

- __Flask-Mail__ for email management
- __threading__ for sending emails asynchronously   
- __Flask-Bootstrap__ for working with HTML-forms
- __Flask-WTF__ and __wtforms__ for working with WEB-forms
- __Flask-SQLAlchemy__ for working with DB models
- __Flask-Migrate__ for migrating DB model (not data)
- __Flask-Moment__ for working with date 
- __Flask-login__ for management user sessions after authentication;
- __Werkzeug__ for password hashing;
- __itsdangerous__ for creating encrypted tokens and validates them

## Additional information

### local Python SMTP server

This is a fake mail server that accepts email messages but instead of sending them, it prints them to the console in a separate terminal.
To run it add these settings for Flask application:
```
config.py:

MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '8025'))
```

or set environment variables:
```
export MAIL_SERVER=localhost
export MAIL_PORT=8025
```

After that open a second terminal session and run the following command on it:

```(venv) $ python -m smtpd -n -c DebuggingServer localhost:8025```

### flask-sqlalchemy
Inserting Records:
```
./manage.py shell
User.query.all()
u1 = User(email='test@example.com', username='test')
db.session.add(u)
db.session.commit()
```

Querying Records:
```
User.query.filter_by(username='test').first()
User.query.filter_by(username='test').first().confirmed
```

Deleting Records:
```
./manage.py shell
u = User(username='test')
db.session.delete(u)
db.session.commit()
```

Deleting Existing Records:
```
./manage.py shell
>>> User.query.all()
[<User 'purple5'>, <User 'test2'>]
>>> User.query.filter_by(username='test2').first().id
10
>>> User.query.filter_by(id=10).delete()
1
>>> User.query.all()
[<User 'purple5'>]
```

### Unit tests
Run unittests:
```
(venv) $ ./manage.py test
test_app_exists (test_basics.BasicsTestCase) ... ok
test_app_is_testing (test_basics.BasicsTestCase) ... ok
test_duplicate_email_change_token (test_user_model.UserModelTestCase) ... ok
test_expired_confirmation_token (test_user_model.UserModelTestCase) ... ok
test_valid_reset_token (test_user_model.UserModelTestCase) ... ok
----------------------------------------------------------------------
Ran 5 tests in 9.171s

OK

```
