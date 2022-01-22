import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    '''Test models for Messages.'''

    def setUp(self):
        '''Create test client, add sample data.'''
        db.drop_all()
        db.create_all()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 7777
        self.testuser.id = self.testuser_id

        self.testuser = User.query.get(self.testuser_id)
        
        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        '''Does basic model work?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.testuser.messages), 1)
        self.assertEqual(self.testuser.messages[0].text, 'Test message 1.')

    def test_like_message(self):
        '''Does like a message work?'''

        message = Message(id=11111, text='Test message 1.', user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        user1 = User.signup('TestUser1', 'email1@email.com', 'password1', 'https://images.freeimages.com/images/small-previews/81e/number-one-1504449.jpg')
        user1_id = 11111
        user1.id = user1_id

        db.session.add_all([message, user1])
        db.session.commit()

        user1.likes.append(message)
        
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == user1_id).all()
        self.assertEqual(len(like), 1)

