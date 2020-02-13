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

        self.new_question = {
            'question': 'What is the main capital of Germany?',
            'answer': 'Berlin',
            'difficulty': 3,
            'category': 3
        }

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
    HTTP Method checks
    """
    def check_200(self, res, data):
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def check_400(self, res, data):
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def check_404(self, res, data):
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def check_405(self, res, data):
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def check_422(self, res, data):
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    def check_500(self, res, data):
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'internal server error')

    def check_503(self, res, data):
        self.assertEqual(res.status_code, 503)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'service unavailable')

    '''
    Tests
    '''
    def test_200_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], dict)
        
    def test_200_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], dict)

    def test_404_get_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.check_404(res, data)

    def test_200_get_questions_by_category(self):
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

    def test_404_get_questions_based_on_category_beyond_valid_page(self):
        res = self.client().get('/categories/3/questions?page=1000')
        data = json.loads(res.data)

        self.check_404(res, data)

    def test_200_get_questions_by_category_with_request_parameter(self):
        res = self.client().get('/categories/2/questions?page=1')
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(data['current_category'], 2)

    def test_200_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['created_id'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']) >= 1)
        self.assertTrue(data['total_questions'] >= len(data['questions']))
        self.assertTrue(data['categories'])

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1', json=self.new_question)
        data = json.loads(res.data)

        self.check_405(res, data)

        res = self.client().post('/questions/1000', json=self.new_question)
        data = json.loads(res.data)

        self.check_405(res, data)

    def test_200_delete_question(self):
        question_id = 36
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()
        
        self.check_200(res, data)
        self.assertEqual(question, None)
        self.assertEqual(data['deleted_id'], question_id)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        
    def test_422_delete_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.check_422(res, data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()