from webapp.extensions import db
from webapp.util_sqlalchemy import SQLALCHEMYOPS
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import abort


class TodoTable(db.Model):
    __tablename__ = 'todotable'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(12), unique=True)
    description = db.Column(db.String(30))

    @classmethod
    def get_all_tasks(cls):
        d = TodoTable.query.all()
        if d:
            return SQLALCHEMYOPS.to_jsonify(res=d)

        return False

    @classmethod
    def get_task_by_task(cls, taskname):
        d = TodoTable.query.filter(TodoTable.task == taskname).first()
        if d:
            return SQLALCHEMYOPS.to_jsonify(res=d)

        return False

    @classmethod
    def delete_task_by_task(cls, taskname):
        TodoTable.query.filter(TodoTable.task == taskname).delete()
        db.session.commit()
        return True

    @classmethod
    def add_a_record_to_table(cls, taskname, taskdescription):
        r = TodoTable(task=taskname, description=taskdescription)
        db.session.add(r)
        db.session.commit()
        return cls.get_task_by_task(taskname=taskname)

    @classmethod
    def update_a_record_by_task(cls, task, taskname, taskdescription):
        try:
            r = TodoTable.query.filter(TodoTable.task == task).first()
            r.task=taskname
            r.description=taskdescription
            db.session.add(r)
            db.session.commit()
            return cls.get_task_by_task(taskname=taskname)
        except SQLAlchemyError as e:
            abort(404, message=str(e))
