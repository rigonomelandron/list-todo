from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, BooleanField
from wtforms.validators import DataRequired, URL
from wtforms.fields.html5 import DateField
from flask_ckeditor import CKEditorField


##WTForm
class CreateTodoList(FlaskForm):
    title = StringField("Todo list Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    date = DateField('DatePicker', format='%Y-%m-%d')
    submit = SubmitField("Submit List")


class CreateTodo(FlaskForm):
    todo_name = StringField("Todo list Title", validators=[DataRequired()])
    done = BooleanField('Done')
    text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Todo")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")
