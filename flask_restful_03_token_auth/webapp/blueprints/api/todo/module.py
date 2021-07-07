from flask_restful import reqparse, abort, Api, Resource
from webapp.extensions import db
from webapp.blueprints.api.todo.tables import TodoTable


def abort_if_not_args(args=None):
    if not args:
        abort(404, message="missing arguments dict")
    return True

def abort_if_todo_doesnt_exist(task):
    d = TodoTable.get_task_by_task(taskname=task)
    if not d:
        abort(404, message="Todo {} doesn't exist".format(task))
    return d

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('task', required=True, help="task is requrired field", case_sensitive=False)
parser.add_argument('desc', required=True, help="desc is requrired field", case_sensitive=False)


def to_dict(d):
    d = d.__dict__
    d.pop('_sa_instance_state')
    return d

# TodoInit
class TodoInit(Resource):
    def post(self):
        d = {
            'task1': 'Pickup Groceries',
            'task2': 'Mail subscription letters',
            'task3': 'Workout for an hour',
        }
        for k,v in d.items():
            r = TodoTable(task=k, description=v)
            db.session.add(r)
            db.session.commit()

        return {'result': 'success'}, 201

# Todo
class Todo(Resource):
    def get(self, task):
        d = abort_if_todo_doesnt_exist(task=task)
        return d

    def delete(self, task):
        abort_if_todo_doesnt_exist(task)
        TodoTable.delete_task_by_task(taskname=task)
        return {"taskid": task, "action": "deleted"}, 204

    def put(self, task):
        args = parser.parse_args()
        abort_if_todo_doesnt_exist(task)
        abort_if_not_args(args=args)
        d = TodoTable.update_a_record_by_task(task=task, taskname=args['task'], taskdescription=args['desc'])
        return d, 201

# TodoList
class TodoList(Resource):
    def get(self):
        d = TodoTable.get_all_tasks()
        return d

    def post(self):
        args = parser.parse_args()
        # args = {"task": "task4", "desc": "Learn how to fly"}
        abort_if_not_args(args=args)
        d = TodoTable.add_a_record_to_table(taskname=args['task'], taskdescription=args['desc'])
        # d = to_dict(d)
        return d, 201
