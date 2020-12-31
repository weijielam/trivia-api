import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    # CORS setup, allows all origins
    CORS(app, resources={'/': {'origins': '*'}})
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response    
    
    @app.route('/categories')
    def get_categories():
        '''
        Handles GET requests for getting all categories
        '''
        # get all categories
        categories = Category.query.all()
        data = {}

        # abort if no categories
        if len(categories) == 0:
            abort(404)
        
        for category in categories:
            data[category.id] = category.type    

        return jsonify({
            'success': True,
            'categories': data
        })

    @app.route('/questions')
    def get_questions():
        '''
        Handles GET requests for getting all questions
        '''
        # get all questions + paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # abort if no questions
        if total_questions == 0:
            abort(404)

        # get all categories
        categories = Category.query.all()
        categories_data = {}
        for category in categories:
            categories_data[category.id] = category.type
            
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_data
        })
    
    # utility for paginating questions
    def paginate_questions(request, selection):
        # get current page and range
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # return questions from selection 
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        '''
        Handles DELETE requests for deleting question by id
        '''
        try:
            # get question by id
            question = Question.query.get(id)
            
            # abort if question not found
            if question is None:
                abort(404)
            
            # delete the question
            question.delete()

            # return success response
            return jsonify({
                'success': True,
                'message': "Question successfully deleted.",
                'deleted': id
            })
        except:
            # abort unprocessable if error
            abort(422)

    @app.route('/questions', methods=['POST'])    
    def create_question():
        try:
            '''
            Handles POST request for creatung new question 
            '''
            # load data from request
            data = request.get_json()
            question = data['question']
            answer = data['answer']
            difficulty = data['difficulty']
            category = data['category']

            # data validation
            if((question == '') or (answer == '') or (difficulty == '') or (category == '')):
                abort(422)

            # create and insert new question
            new_question = Question(
                                question=question,
                                answer=answer,
                                difficulty=difficulty,
                                category=category)

            new_question.insert()

            # return success response
            return jsonify({
                'success': True,
                'message': 'Question successfully created!'
            }), 201

        except:
            # abort unprocessable if error
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            # load data from request
            data = request.get_json()
            search_term = data['searchTerm']
            
            # query database using search term
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            
            # no questions returns a 404 error
            if len(questions) == 0:
                abort(404)
            
            # paginate the response from database query
            paginated_questions = paginate_questions(request, questions)

            # return success response
            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            }), 200
        
        except:
            # abort unprocessable if error
            abort(422)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_categories(id):
        # get category by id
        category = Category.query.filter_by(id=id).one_or_none()

        # data validation
        if (category is None):
            abort(422)
        
        # get questions by category id
        questions = Question.query.filter_by(category = id).all()

        # paginate the response from database query
        paginated_questions = paginate_questions(request, questions)

        # return success response
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category.type 
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz_question():
        try:
            # load data from request
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']

            # loads all questions if "ALL" is selected
            # else return questions from category specified by id
            if(quiz_category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=quiz_category['id']).all()
            
            # pick a random question
            def get_random_question():
                return questions[random.randint(0, len(questions)-1)]

            next_question = get_random_question()
            found = True

            # if question was previously asked, pick a new random question
            while found:
                if next_question.id in previous_questions:
                    next_question = get_random_question()
                else:
                    found = False

            # return success response
            return jsonify({
                'success': True,
                'question': next_question.format(),
            }), 200
        except:
            # abort bad request if error
            abort(400)

    '''Error Handling'''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request.'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found.'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422, 
            'message': 'Unprocessable entity.'
        }), 422

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500, 
            'message': 'Internal server error. Please try again later.'
        }), 500
    
    return app

        