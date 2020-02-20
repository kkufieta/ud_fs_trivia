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

        self.searchTerm = {
            'searchTerm': 'boxer'
        }

        self.play_quiz_json_category_all = {
            'previous_questions': [],
            'quiz_category': {'type': 'ALL', 'id': 0}
        }

        self.play_quiz_json_category_1 = {
            'previous_questions': [20, 21],
            'quiz_category': {'type': 'Science', 'id': 1}
        }

        self.play_quiz_question_id_category_1 = 22;

        self.play_quiz_json_category_2 = {
            'previous_questions': [16, 17],
            'quiz_category': {'type': 'Art', 'id': 2}
        }

        self.play_quiz_question_possible_ids_category_2 = [18, 19];

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

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1', json=self.new_question)
        data = json.loads(res.data)

        self.check_405(res, data)

        res = self.client().post('/questions/1000', json=self.new_question)
        data = json.loads(res.data)

        self.check_405(res, data)

    def test_200_create_and_delete_question(self):
        # Create a question, test if it works properly
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['created_id'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']) >= 1)
        self.assertTrue(data['total_questions'] >= len(data['questions']))
        self.assertTrue(data['categories'])

        # Save id of created question so we can delete it
        created_id = data['created_id']

        # Test if deleting a question works properly
        res = self.client().delete('/questions/' + str(created_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == created_id).one_or_none()
        
        self.check_200(res, data)
        self.assertEqual(question, None)
        self.assertEqual(data['deleted_id'], created_id)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        
    def test_422_delete_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.check_422(res, data)

    def test_200_search_for_question(self):
        res = self.client().post('/questions', json=self.searchTerm)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        self.assertEqual(int(data['current_category']), 0)
        self.assertEqual(len(data['questions']), 1)

    def test_200_play_quiz(self):
        # Test with all categories
        res = self.client().post('/quizzes', json=self.play_quiz_json_category_all)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['question'])

        # Test with category 1
        res = self.client().post('/quizzes', json=self.play_quiz_json_category_1)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], self.play_quiz_question_id_category_1)

        # Test with category 2
        res = self.client().post('/quizzes', json=self.play_quiz_json_category_2)
        data = json.loads(res.data)

        self.check_200(res, data)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] in
                        self.play_quiz_question_possible_ids_category_2)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()