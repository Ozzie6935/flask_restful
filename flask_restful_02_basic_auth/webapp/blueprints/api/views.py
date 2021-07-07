from flask import Blueprint
from flask_restful import Api
from webapp.blueprints.api.todo.module import Todo, TodoList, TodoInit
from webapp.blueprints.api.auth.auth import UserInit, UserAuth, AdminAuth


api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp)

api.add_resource(TodoInit, '/todos/init') ## adds some records
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:task>')



### First add user with example below
## Creat new User -- Not behind login_required decorator
# curl http://127.0.0.1:8080/api/v1/user/init \
# -X POST -H "Content-Type: application/json" \
# -d '{"username":"ozzie","password":"abc123", "admin": "True"}'
## or
## -d '{"username":"mark","password":"abc123"}'
# # --header "X-Vault-Token: $VAULT_TOKEN" \
api.add_resource(UserInit, '/user/init')


### Second query user with authentiction
## This will fail:
## curl -i -X GET http://127.0.0.1:8080/api/v1/user/get_my_data
##
## This will succeed:
## curl -i -X GET -u ozzie:abc123 http://127.0.0.1:8080/api/v1/user/get_my_data
api.add_resource(UserAuth, '/user/get_my_data')

## behind authentiction and admin required
api.add_resource(AdminAuth, '/user/get_my_data/<string:user>')
