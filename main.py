from flask import Flask, render_template, redirect, url_for, request, session, jsonify, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Task
from forms import LoginForm, RegistrationForm, TaskForm
import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = b'f3e171cfa5c1f4f65be19ac8e485913682afbad57d81d506fb4eb6d68bd948f3'
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planerdb.db'

db.init_app(app)


login_manager = LoginManager()
login_manager.login_view = 'enter'
login_manager.init_app(app)



@app.cli.command("init-db")
def init_db():
    db.create_all()
    print('Well Done!')

#
# @app.cli.command("fill-db")
# def feel_tables():
#     count = 6
#     for user in range(1, count+1):
#         new_user = User(username=f'user{user}', email=f'user{user}@example.com', password=f'qwerty{user}')
#         db.session.add(new_user)
#     db.session.commit()
#     print('done Users!!!')
#     for task in range(1, count**2):
#         author = User.query.filter_by(username=f'user{task % count + 1}').first()
#         new_task = Task(title= f'Post title {task}', content=f'Task description {task}', author=author)
#         db.session.add(new_task)
#     db.session.commit()
#     print('done Tasks!!!')

#
# @app.cli.command("edit-task")
# def edit_user():
#     task = Task.query.get(10)
#     task.title = 'New Title!!!'
#     task.content = 'new_email@example.com'
#     # task.deadline = "2024-02-11"
#     db.session.commit()
#     print('Edit Task Content in DB!')


@app.route('/')
def index():
    return redirect(url_for('main'))


@app.route('/main/')
def main():
    return render_template('index.html')


@app.route('/log/', methods=['GET', 'POST'])
def log():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        session['username'] = request.form.get('username')
        session['email'] = request.form.get('email')
        session['password'] = request.form.get('password')
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('login.form.html', form=form)
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('login.form.html', form=form)
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('login.form.html', form=form)


@app.route('/enter/', methods=['GET', 'POST'])
def enter():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        session['username'] = request.form.get('username')
        session['password'] = request.form.get('password')
        remember = True if request.form.get('remember') else False
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if not user or not user.password == password:
            print('Please check your login details and try again.')
            return render_template('enter.html', form=form)
        login_user(user)
        return redirect(url_for('main'))
    return render_template('enter.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/create_tasks/', methods=['GET', 'POST'])
@login_required
def create_tasks():
    form = TaskForm()
    if request.method == 'POST' and form.validate():
        session['title'] = request.form.get('title')
        session['content'] = request.form.get('content')
        session['start'] = request.form.get('start')
        session['deadline'] = request.form.get('deadline')
        title = form.title.data
        content = form.content.data
        start = form.start.data
        deadline = form.deadline.data
        deadLine_calendar = deadline + datetime.timedelta(days=1)
        task = Task(title=title, content=content, start = start, deadline=deadline,deadLine_calendar=deadLine_calendar, author_id=current_user.id)
        try:
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('tasks'))
        except:
            print("Error")
    return render_template('create_task.html', form=form)


@app.route('/tasks/')
@login_required
def tasks():
    tasks = Task.query.filter_by(author_id=current_user.id)
    context = {'tasks': tasks}
    return render_template('Task_list.html', **context)

@app.route('/tasks/<int:id>/del')
def task_del(id):
    task = Task.query.get(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('tasks'))
    except:
        return "Error"

@app.route('/tasks/<int:id>/change', methods=['GET', 'POST'])
@login_required
def change_tasks(id):
    form = TaskForm()
    task = Task.query.get(id)
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.content = request.form.get('content')
        date_time_obj_start = datetime.datetime.strptime(request.form.get('start'), '%Y-%m-%d')
        task.start = date_time_obj_start.date()
        date_time_obj_deadline = datetime.datetime.strptime(request.form.get('deadline'), '%Y-%m-%d')
        task.deadline = date_time_obj_deadline.date()
        task.deadLine_calendar = task.deadline + datetime.timedelta(days=1)
        db.session.commit()
        return redirect(url_for('tasks'))
    elif request.method == "GET":
        form.title.data = task.title
        form.content.data = task.content
        form.start.data = task.start
        form.deadline.data = task.deadline
    return render_template('change_task.html', task=task, form=form)



@app.route('/calendar/')
@login_required
def calendar():
    tasks = Task.query.filter_by(author_id=current_user.id)
    context = {'tasks': tasks}
    return render_template('calendar.html', **context)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    print("LOGOUT Successfully")
    return redirect(url_for('main'))




if __name__ == "__main__":
    app.run(host='0.0.0.0')


