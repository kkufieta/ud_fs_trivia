import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    def check_404(self, res, data):
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def check_200(self, res, data):
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], dict)
        
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], dict)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.check_404(res, data)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(data['current_category'], 1)

    def test_404_get_questions_invalid_category_id(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.check_404(res, data)

        res = self.client().get('/categories/-1/questions')
        data = json.loads(res.data)

        self.check_404(res, data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()