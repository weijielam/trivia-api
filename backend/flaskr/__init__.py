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
  
  '''
  @TODO COMPLETED: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})
  '''
  @TODO COMPLETED: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response  
  '''
  @TODO COMPLETED: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    data = {}

    if len(categories) == 0:
      abort(404)
    
    for category in categories:
      data[category.id] = category.type  

    print(data)
    return jsonify({
      'success': True,
      'categories': data
    })

  '''
  @TODO WIP: may need to clean up 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
  
    # get all questions + paginate
    selection = Question.query.all()
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)

    # abort if no questions
    if total_questions == 0:
      abort(404)

    # get all categories
    categories = Category.query.all()
    categories_data = {} # possibly needs to be renamed
    for category in categories:
      categories_data[category.id] = category.type
      
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'categories': categories_data
    })
  
  '''
  @TODO DONE
  CUSTOM: return QUESTIONS_PER_PAGE
  '''
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      
      if question is None:
        abort(404)
      
      question.delete()

      return jsonify({
        'success': True,
        'deleted': id
      })
    except:
      abort(422)
  '''
  @TODO WIP: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])  
  def create_question():
    try:
      data = request.get_json()
      question = data['question']
      answer = data['answer']
      difficulty = data['difficulty']
      category = data['category']

      # data validation
      if((question is None) or (answer is None) or (difficulty is None) or (category is None)):
        abort(422)

      new_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)

      new_question.insert()

      return jsonify({
        'success': True,
        'message': 'Question successfully created!'
      }), 201

    except:
      abort(422)
  '''
  @TODO WIP: On frontend need to implement route for question search 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      print('hello world')
      data = request.get_json()
      print(data)
      search_term = data['searchTerm']
      
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      
      # no questions returns a 404 error
      if len(questions) == 0:
        abort(404)
      
      paginated_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(Question.query.all())
      }), 200
    
    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_categories(id):

    category = Category.query.filter_by(id=id).one_or_none()

    if (category is None):
      abort(422)
    
    questions = Question.filter_by(category = id).all()

    paginated_questions = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(questions),
      'current_category': category.type 
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz_question():
    data = request.get_json()
    previous_question = data['previous_questions']
    quiz_category = data['quiz_category']

    if((quiz_category is None) or (previous_questions is None)):
      abort(400)
    
    # default value -> return all questions
    # else return questions from category
    if(quiz_category['id'] == 0):
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=category['id']).all()

    def get_random_question():
      return questions[random.randint(0, len(questions)-1)]

    next_question = get_random_question()
    found = True

    while found:
      if next_question.id in previous_questions:
        next_question = get_random_question()
      else:
        found = False

    return jsonify({
      'success': True,
      'question': next_question.format(),
    }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found. Input out of range.'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422, 
      'message': 'unprocessable. Synax error.'
    }), 422

  @app.errorhandler(500)
  def internal_server(error):
    return jsonify({
      'success': False,
      'error': 500, 
      'message': 'Sorry, the falut is us not you. Please try again later.'
    }), 500
  
  return app

    