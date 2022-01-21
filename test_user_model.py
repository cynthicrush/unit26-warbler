"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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
        user1_id = 1111
        user1.id = user1_id

        user2 = User.signup('TestUser2', 'email2@email.com', 'password2', 'https://images.freeimages.com/images/small-previews/d63/two-1233942.jpg')
        user2_id = 2222
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1.id)
        user2 = User.query.get(user2.id)

        self.user1 = user1
        self.user1_id = user1_id
        self.user2 = user2
        self.user1_id = user2_id

        self.client = app.test_client()

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

        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))