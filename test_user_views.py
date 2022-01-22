import os
from unittest import TestCase

from models import db, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    '''Test views for users.'''

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

        user1 = User.signup('TestUser1', 'email1@email.com', 'password1', 'https://images.freeimages.com/images/small-previews/81e/number-one-1504449.jpg')
        user1_id = 11111
        user1.id = user1_id

        user2 = User.signup('TestUser2', 'email2@email.com', 'password2', 'https://images.freeimages.com/images/small-previews/d63/two-1233942.jpg')
        user2_id = 22222
        user2.id = user2_id

        user3 = User.signup('TestUser3', 'email3@email.com', 'password3', 'https://images.freeimages.com/images/small-previews/10d/house-number-1199629.jpg')
        user3_id = 33333
        user3.id = user3_id

        self.user1 = user1
        self.user1_id = user1_id
        self.user2 = user2
        self.user2_id = user2_id
        self.user3 = user3
        self.user3_id = user3_id

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def setup_follows(self):
        '''Set up some followings and followers.'''
        follows1 = Follows(user_following_id=self.testuser_id, user_being_followed_id=self.user1_id)
        follows2 = Follows(user_following_id=self.testuser_id, user_being_followed_id=self.user2_id)
        follows3 = Follows(user_following_id=self.user1_id, user_being_followed_id=self.testuser_id)

        db.session.add_all([follows1, follows2, follows3])
        db.session.commit()

    def test_show_followers_page(self):
        '''
            When you are logged in, can you see the follower page for any user?
        '''
        self.setup_follows()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.get(f'/users/{self.testuser_id}/followers')

            self.assertIn('TestUser1', str(response.data))
            self.assertNotIn('TestUser2', str(response.data))

    def test_show_followings_page(self):
        '''
            When you are logged in, can you see the following page for any user?
        '''
        self.setup_follows()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.get(f'/users/{self.testuser_id}/following')

            self.assertIn('TestUser1', str(response.data))
            self.assertIn('TestUser2', str(response.data))
            self.assertNotIn('TestUser3', str(response.data))

    def test_show_unauthorized_followers_page(self):
        '''
            When you are logged out, are you disallowed from visiting a user is follower pages?
        '''

        self.setup_follows()
        with self.client as c:

            response = c.get(f'/users/{self.testuser_id}/followers', follow_redirects=True)
            self.assertEqual(response.status_code, 404)
            self.assertNotIn('testuser', str(response.data))
            self.assertIn('Access unauthorized', str(response.data))

    def test_show_unauthorized_followings_page(self):
        '''
            When you are logged out, are you disallowed from visiting a user is following pages?
        '''

        self.setup_follows()
        with self.client as c:

            response = c.get(f'/users/{self.testuser_id}/followings', follow_redirects=True)
            self.assertEqual(response.status_code, 404)
            self.assertNotIn('testuser', str(response.data))
            self.assertIn('Access unauthorized', str(response.data))


