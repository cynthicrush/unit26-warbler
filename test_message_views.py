"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 7777
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        '''When you're logged in, can you delete a message as yourself?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.post('/messages/11111/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            message = Message.query.get(11111)
            self.assertIsNone(message)

    def test_unauthenticated_message_add(self):
        '''When you're logged out, are you prohibited from adding messages?'''

        with self.client as c:
            response = c.post('/messages/new', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', str(response.data))

    def test_unauthenticated_message_delete(self):
        '''When you're logged out, are you prohibited from deleting messages?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            response = c.post('/messages/11111/delete', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', str(response.data))
    
    def test_unauthorizated_message_add(self):
        '''When you’re logged in, are you prohibiting from adding a message as another user?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        user = User.signup(username='Unauthorizated', email='email@email.com', password='password', image_url=None)
        user.id = 77777

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 77777

            response = c.post('/messages/new', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', str(response.data))

    def test_unauthorizated_message_delete(self):
        '''When you’re logged in, are you prohibiting from adding a message as another user?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        user = User.signup(username='Unauthorizated', email='email@email.com', password='password', image_url=None)
        user.id = 77777

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 77777

            response = c.post('/messages/11111/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', str(response.data))

