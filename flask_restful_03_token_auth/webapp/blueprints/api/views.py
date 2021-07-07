from flask import Blueprint
from flask_restful import Api
from webapp.blueprints.api.todo.module import Todo, TodoList, TodoInit
from webapp.blueprints.api.auth.auth import UserInit, UserAuth, AdminAuth, AuthToken, UserAuthToken, ClientInit


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
# curl -i -X GET http://127.0.0.1:8080/api/v1/user/get_my_data -u ozzie:abc123
# curl -i -X GET http://127.0.0.1:8080/api/v1/user/get_my_data -u monitoring00:0c86d864c92c856f523a6c6b
# curl -i -X GET http://127.0.0.1:8080/api/v1/user/get_my_data -u etl00:b6aa514212d881646afba5ab
api.add_resource(UserAuth, '/user/get_my_data')



## behind authentiction and admin required
api.add_resource(AdminAuth, '/user/get_my_data/<string:user>')



#### Token
# Onboard a client
# curl -i -X POST \
# http://127.0.0.1:8080/api/v1/client/init \
# -H "Content-Type: application/json" \
# -d '{"client_id":"monitoring00", "admin": "True"}'
# [
#     {
#         "id": 1,
#         "username": null,
#         "client_id": "monitoring00",
#         "client_secret": "aaa35ef0b74b93bde5fd51ba",
#         "admin": true
#     }
# ]
api.add_resource(ClientInit, '/client/init')


# curl -i -X POST \
# http://127.0.0.1:8080/api/v1/as/token.oauth2 \
# -u monitoring00:0c86d864c92c856f523a6c6b \
# -H "Content-Type: application/json" \
# -d '{"grant_type":"client_credentials"}'

# curl -i -X POST \
# http://127.0.0.1:8080/api/v1/as/token.oauth2 \
# -u ozzie:abc123 \
# -H "Content-Type: application/json" \
# -d '{"grant_type":"user_credentials"}'
api.add_resource(AuthToken, '/as/token.oauth2')

# curl -i -X GET http://127.0.0.1:8080/api/v1/client/get_my_data/token --header "Authorization:Bearer $token"
api.add_resource(UserAuthToken, '/client/get_my_data/token')
