from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    tasks = db.relationship('Task', backref='author', lazy=True)

    def __repr__(self):
        return f'User({self.username}, {self.email})'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    start = db.Column(db.Date, default=datetime.date.today())
    deadline = db.Column(db.Date, default=datetime.date.today() + datetime.timedelta(days=3))
    deadLine_calendar = db.Column(db.Date, default = None)
    # priority = db.column(db.Integer)

    def __repr__(self):
        return f'Task({self.title}, {self.content}, {self.deadline})'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deadline = db.Column(db.Date, default=datetime.date.today() + datetime.timedelta(days=3))

    def __repr__(self):
        return f'Project({self.title}, {self.content}, {self.deadline})'
