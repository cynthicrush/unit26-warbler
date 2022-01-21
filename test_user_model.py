"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py
#    FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup('TestUser1', 'email1@email.com', 'password1', 'https://images.freeimages.com/images/small-previews/81e/number-one-1504449.jpg')
        user1_id = 11111
        user1.id = user1_id

        user2 = User.signup('TestUser2', 'email2@email.com', 'password2', 'https://images.freeimages.com/images/small-previews/d63/two-1233942.jpg')
        user2_id = 22222
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1.id)
        user2 = User.query.get(user2.id)

        self.user1 = user1
        self.user1_id = user1_id
        self.user2 = user2
        self.user1_id = user2_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):
        '''
            Does is_following successfully detect when user1 is following user2?
            Does is_following successfully detect when user1 is not following user2?
        '''

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        '''
            Does is_followed_by successfully detect when user1 is followed by user2?
            Does is_followed_by successfully detect when user1 is not followed by user2?
        '''

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_invalid_signup(self):
        '''Does User.create successfully create a new user given valid credentials?'''

        new_test_user = User.signup('NewTestUser', 'newtestuser@email.com', 'password3', 'https://images.freeimages.com/images/small-previews/10d/house-number-1199629.jpg')
        new_test_user_id = 3333
        new_test_user.id = new_test_user_id

        db.session.commit()

        new_test_user = User.query.get(new_test_user_id)

        self.assertEqual(new_test_user.username, 'NewTestUser')
        self.assertEqual(new_test_user.email, 'newtestuser@email.com')
        self.assertEqual(new_test_user.image_url, 'https://images.freeimages.com/images/small-previews/10d/house-number-1199629.jpg')
        self.assertNotEqual(new_test_user.password, 'password3')
        self.assertTrue(new_test_user.password.startswith('$2b$'))

    def test_invalid_signup(self):
        '''Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?'''

        invalid = User.signup('TestUser2', 'email2@email.com', 'password3', None)
        invalid_user_id = 4444
        invalid.id = invalid_user_id

        empty_invalid = User.signup('', '', 'password3', None)
        invalid_empty_user_id = 4444
        empty_invalid.id = invalid_empty_user_id
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
        with self.assertRaises(ValueError) as context:
            User.signup('TestUser3', 'email3@email.com', None, None)
            User.signup('TestUser3', 'email3@email.com', '', None)

    def test_invalid_authentication(self):
        '''
            Does User.authenticate successfully return a user when given a valid username and password?
            Does User.authenticate fail to return a user when the username is invalid?
            Does User.authenticate fail to return a user when the password is invalid?
        '''

        user1 = User.authenticate(self.user1.username, 'password1')
        self.assertEqual(user1.id, self.user1_id)
        self.assertFalse(User.authenticate('WrongUsername', 'password1'))
        self.assertFalse(User.authenticate(self.user1.username, 'WrongPassword'))

