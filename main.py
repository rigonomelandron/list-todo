# main

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import LoginForm, RegisterForm, CreateTodo, CreateTodoList

app = Flask(__name__)
app.config["SECRET_KEY"] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLES

class TodoList(db.Model):
    __tablename__ = "todo_list"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="list")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)

    todo = relationship("Todo", back_populates="parent_list", cascade="all, delete",
                        passive_deletes=True)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    todo = relationship("Todo", back_populates="todo_author")
    list = relationship("TodoList", back_populates="author")


class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey("todo_list.id", ondelete="CASCADE"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    todo_name = db.Column(db.String(250), nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    text = db.Column(db.Text, nullable=False)

    parent_list = relationship("TodoList", back_populates="todo")
    todo_author = relationship("User", back_populates="todo")


db.create_all()


@app.route('/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            print("not user")
            flash("That email does not exist, please try again or register.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))

        else:
            login_user(user)
            return redirect(url_for('get_all_list'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/get_all_list')
def get_all_list():
    lists = TodoList.query.filter_by(author_id=current_user.id).all()

    return render_template('all_list.html', lists=lists, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_list"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/new_list', methods=["GET", "POST"])
def new_list():
    form = CreateTodoList()
    if form.validate_on_submit():
        new_list = TodoList(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=current_user,
            date=form.date.data,
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("get_all_list"))

    return render_template("new_list.html", form=form, current_user=current_user)


@app.route('/new_todo/<int:id_list>', methods=["GET", "POST"])
def new_todo(id_list):
    form = CreateTodo()

    list = TodoList.query.get(id_list)

    if form.validate_on_submit():
        new_todo = Todo(
            todo_name=form.todo_name.data,
            parent_list=list,
            done=form.done.data,
            text=form.text.data,
            todo_author=current_user,

        )
        db.session.add(new_todo)
        db.session.commit()
        form.todo_name.data = ""
        form.done.data = False
        form.text.data = ""
        return render_template("new_todo.html", form=form, current_user=current_user, list=list)

    return render_template("new_todo.html", form=form, current_user=current_user, list=list)


@app.route('/list_todo/<int:id_list>', methods=["GET", "POST"])
def list_todo(id_list):
    list = TodoList.query.filter_by(id=id_list).first()
    todos = Todo.query.filter_by(list_id=id_list).all()
    return render_template("list_todo.html", list=list, todos=todos)


@app.route("/update_done/<int:id_todo>", methods=["GET", "POST", "PATCH"])
def update_done(id_todo):
    print(id_todo)
    todo = Todo.query.filter_by(id=id_todo).first()
    if todo.done:
        todo.done = False
    else:
        todo.done = True
    db.session.commit()
    list = TodoList.query.filter_by(id=todo.list_id).first()
    todos = Todo.query.filter_by(list_id=todo.list_id).all()
    return render_template("list_todo.html", list=list, todos=todos)


@app.route("/delete_todo/<int:id_todo>", methods=["GET", "DELETE"])
def delete_todo(id_todo):
    todo = Todo.query.filter_by(id=id_todo).first()

    if todo:
        db.session.delete(todo)
        db.session.commit()
    list = TodoList.query.filter_by(id=todo.list_id).first()
    todos = Todo.query.filter_by(list_id=todo.list_id).all()
    return render_template("list_todo.html", list=list, todos=todos)


@app.route("/delete_list/<int:id_list>", methods=["GET", "DELETE"])
def delete_list(id_list):
    list = TodoList.query.filter_by(id=id_list).first()
    if list:
        db.session.delete(list)
        db.session.commit()
    lists = TodoList.query.all()

    return render_template('all_list.html', lists=lists, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
