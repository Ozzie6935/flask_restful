from flask import Blueprint
from flask_restful import Api
from webapp.blueprints.api.todo.module import Todo, TodoList, TodoInit


api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp)

api.add_resource(TodoInit, '/todos/init') ## adds some records
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:task>')
