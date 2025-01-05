from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ProfileForm(FlaskForm):
    name = StringField("Name")
    email = StringField("Email", validators=[Email()])
    phone_nr = StringField("Phone Number", validators=[Regexp(r'^0[1-9][0-9]{8}$', message="Invalid phone number.")])
    age = StringField("Age", validators=[Regexp(r'^[1-9][0-9]$')])
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    newPassword = PasswordField("New Password", validators=[DataRequired()])
    repeatNewPassword = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo('newPassword', message="Passwords must match")])
    submit = SubmitField("Change Password")
