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
    TODO - will need to add comments/documentation
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
    
    # 
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # make assertions of response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

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
    
    def test_create_new_question(self):
        test_data = {
            'question': 'This is a test question',
            'answer': 'This is a test answer',
            'difficulty': 1,
            'category': 1,
        }

        response = self.client().post('/questions', json=test_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully created!")
    
    def test_create_new_question_with_empty_data(self):
        test_data = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }
        response = self.client().post('/questions', json=test_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity.")



    def test_get_questions_by_category(self):
        #
        print('test')

    """Error handling tests"""
    #
    #
    #
    #

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()