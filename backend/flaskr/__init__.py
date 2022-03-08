import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import select

from werkzeug.wrappers import response

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selections):
        # Implement pagniation
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        formatted_selections = [selection.format() for selection in selections]
        return formatted_selections[start:end]

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    # @app.after_request
    # def after_request(repsonse):
    #     repsonse.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
    #     repsonse.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
    #     return response
    
    @app.route('/')
    def hello():
      return 'Welcome to the world.'

    @app.route('/categories', methods=['GET'])
    #@cross_origin
    def get_categories():
        """FormView.js---componentDidMount获取所有类别"""
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories':{category.id: category.type for category in categories}
        })
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods=['GET'])
    #@cross_origin
    def get_questions():
        categories = Category.query.order_by(Category.type).all()
        selection =  Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request,selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions':current_questions,
            'total_questions':len(selection),
            'categories':{category.id : category.type for category in categories},
            'current_category':None,
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<question_id>', methods=['DELETE'])
    #@cross_origin
    def delete_question(question_id):
        """QuestionView.js---questionAction"""
        try:
          question = Question.query.get(question_id)
        
          if question is None:
            abort(404)

          question.delete()

          return jsonify({
              'success': True,
              'deleted': question_id,
          })
        except:
          abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        """FormView.js---submitQuestion"""
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,category=new_category,difficulty=new_difficulty)
            question.insert()

            return jsonify({
              'success': True,
              'created': question.id,
            })
        except:
            abort(422)
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """QuestionView.js---submitSearch"""
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        """QuestionView.js---getByCategory"""
        try:
          questions = Question.query.filter(Question.category == str(category_id)).all()
        
          if questions is None:
            abort(404)

          return jsonify({
              'success': True,
              'questions':[question.format() for question in questions],
              'total_questions':len(questions),
              'current_category':category_id
          })
        except:
          abort(404)

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
    def play_quiz():
      """QuizView.js---getNextQuestion"""
      try:
        body = request.get_json()
        quiz_category = body.get('quiz_category',None)
        previous_questions = body.get('previous_questions',None)

        if quiz_category['type'] == 'click':
          questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
        else:
          questions = Question.query.filter_by(
            category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()
        
        new_question = questions[random.randrange(0, len(questions))].format() if len(questions) > 0 else None

        return jsonify({
          'success' : True,
          'question' : new_question
        })
      except:
        abort(422)
        
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': "resource not found"
      }),404

    @app.errorhandler(422)
    def unprocessabe(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': "unprocessabe"
      }),422
    
    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': "bad request"
      }),400
    
    @app.errorhandler(405)
    def method_not_allowed(error):
      return jsonify({
        'success': False,
        'error': 405,
        'message': "method not allowed"
      }),405

    @app.errorhandler(500)
    def internal_error(error):
      return jsonify({
        'success': False,
        'error': 500,
        'message': "internal error"
      }),500
    return app

    