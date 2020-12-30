import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


"""
This function is used in order to avoid having to drop the database when running the test cases
Reference: https://github.com/EmmanuelSage/trivia-api
"""
def create_test_question():
    question = Question(
        question = 'This is a test question that should be deleted',
        answer = 'This is a test answer that should be deleted',
        difficulty = 1,
        category = 1,
    )
    question.insert()

    return question.id

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
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    """GET Categories and Questions Test Cases"""
    def test_get_categories(self):
        # make request and process response
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
    
    def test_get_questions(self):
        # make request and process response
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    """DELETE Question Test Cases"""
    def test_delete_question_success(self):
        # create test question
        test_question_id = create_test_question()

        # delete test question
        response = self.client().delete('/questions/{}'.format(test_question_id))
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted.")
        self.assertEqual(data['deleted'], test_question_id)
    
    def test_delete_question_twice(self):
        # create test question
        test_question_id = create_test_question()
        
        # delete test question
        self.client().delete('/questions/{}'.format(test_question_id))

        # try to delete the same question again
        response = self.client().delete('/questions/{}'.format(test_question_id))
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity.")
    
    def test_delete_question_id_not_exist(self):
        # test id for question does not exist
        response = self.client().delete('/questions/123456789')
        data = json.loads(response.data)
        
        # make assertions of response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity.")
    
    def test_delete_question_with_invalid_id(self):
        # this tests an invalid id
        response = self.client().delete('/questions/asdff3571')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')


    """CREATE Question Test Cases"""
    def test_create_new_question(self):
        # create payload for post request
        test_data = {
            'question': 'This is a test question',
            'answer': 'This is a test answer',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=test_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully created!")
    
    def test_create_new_question_with_empty_data(self):
        # create payload for post request
        test_data = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=test_data)
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity.")


    """Search Questions Test Cases"""
    def test_search_questions(self):
        request_data = { 'searchTerm': 'Tom Hanks' }

        # make request and process response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    """Get questions by category Test Cases"""
    def test_get_questions_by_category(self):
        # make request and process response
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_get_questions_by_category_invalid_id(self):
        # make request and process response
        response = self.client().get('/categories/123456789/questions')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity.")


    """Play quiz questions Test Cases"""
    def test_play_quiz_questions(self):
        # create payload for post requests
        test_data = {
            'previous_questions': [2,4],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 5
            }
        }

        # make request and process response
        response = self.client().post('/quizzes', json=test_data)
        data = json.loads(response.data)

        print('response.data', response.data)
        print('response.status_code', response.status_code)
        print('data', data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'], True)
        
        # assert question is returned & from correct category
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['category'], 4)

        # assert question returned is not on previous question list
        self.assertTrue(data['question']['id'], 2)
        self.assertTrue(data['question']['id'], 4)

    def test_play_quiz_questions_no_data(self):
        # make request and process response. no data is sent
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Bad request.')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()