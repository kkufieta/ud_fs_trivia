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
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  
  # @app.route('/messages')
  # @cross_origin()
  # def get_messages():
    # return 'GETTING MESSAGES'

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  Endpoint that handles GET requests for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
      categories = Category.query.order_by(Category.id).all()
      categories_dict = {}
      for category in categories:
          categories_dict[category.id] = category.type

      return jsonify({
        'success': True,
        'categories': categories_dict
      })

  def paginate_questions(request, questions):
      page = request.args.get('page', 1, type=int)    
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = [question.format() for question in questions]
      current_questions = questions[start:end]
      return current_questions
      
  '''
  Error handlers for all expected errors.
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': 'bad request'
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'error': 404,
          'message': 'resource not found'
      }), 404

  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          'success': False,
          'error': 405,
          'message': 'method not allowed'
      }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
        return jsonify({
          'success': False,
          'error': 422,
          'message': 'unprocessable entity'
        }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
        return jsonify({
          'success': False,
          'error': 500,
          'message': 'internal server error'
        }), 500

  @app.errorhandler(503)
  def service_unavailable(error):
        return jsonify({
          'success': False,
          'error': 503,
          'message': 'service unavailable'
        }), 503
        
  '''
  Endpoint that handles GET requests for questions, including pagination.
  Returns a list of questions, number of total questions, current category,
  and a dict of all categories.
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
        page = request.args.get('page', 1, type=int)    
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        categories_dict = {}
        for category in categories:
              categories_dict[category.id] = category.type

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': '0',
          'categories': categories_dict
        })

  '''
  Endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if not question:
        abort(422)

      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)
      categories = Category.query.order_by(Category.id).all()
      categories_dict = {}
      for category in categories:
            categories_dict[category.id] = category.type

      return jsonify({
        'success': True,
        'deleted_id': question_id,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': categories_dict
      })

    except:
      abort(422)
    

  '''
  Endpoint to POST in order to search for questions based on a search term,
  or to post a new question, which requires the question and answer text,
  category and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()    

    search_term = body.get('searchTerm')
    if search_term:
        questions = Question.query.filter(Question.question.ilike('%' + search_term + '%'))\
          .order_by(Question.id).all()
          # search for questions

        current_questions = paginate_questions(request, questions)

        categories = Category.query.order_by(Category.id).all()
        categories_dict = {}
        for category in categories:
              categories_dict[category.id] = category.type

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': '0',
          'categories': categories_dict
        })
    else:
      question = body.get('question')
      answer = body.get('answer')
      difficulty = body.get('difficulty')
      category = body.get('category')
      if not question or not answer or not difficulty or not category:
            abort(400)

      try:
        question = Question(question=question, answer=answer,
                            difficulty=difficulty, category=category)
                            
        question.insert()

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        categories = Category.query.order_by(Category.id).all()
        categories_dict = {}
        for category in categories:
              categories_dict[category.id] = category.type

        return jsonify({
          'success': True,
          'created_id': question.id,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': '0',
          'categories': categories_dict
        })

      except:
        abort(422)
  
  '''
  Handles not allowed new question post request to specific question endpoint.
  '''
  @app.route('/questions/<int:question_id>', methods=['POST'])
  def question_created_not_allowed(question_id):
    abort(405)


  '''
  GET endpoint to get questions based on category.
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_of_category(category_id):
    category_ids = Category.query.with_entities(Category.id).all()
    category_ids = [category_id_num[0] for category_id_num in category_ids]
    if category_id not in category_ids:
          abort(404)
    questions = Question.query.join(Category, Question.category == category_id).order_by(Question.category).all()
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
          abort(404)
    total_questions = len(questions)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'current_category': category_id
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
  def get_questions_to_play_quiz():
    body = request.get_json()    
    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')
    print(previous_questions)
    print(quiz_category, type(quiz_category))
    category_id = quiz_category['id']
    if category_id == 0:
      question_ids = Question.query.with_entities(Question.id).all()
    else:
      question_ids = Question.query.filter(Question.category == category_id).\
        with_entities(Question.id).all()
    question_ids = [question[0] for question in question_ids]
    question = None
    while not question and len(question_ids) > 0:
      random_index = random.randint(0, len(question_ids) - 1)
      if question_ids[random_index] in previous_questions:
        question_ids.pop(random_index)
      else:
        question = Question.query.filter(Question.id == question_ids[random_index]).one_or_none()
        return jsonify({
          'success': True,
          'question': question.format()
        })
      
    return jsonify({
      'success': True,
      'question': None
      })

  return app

    