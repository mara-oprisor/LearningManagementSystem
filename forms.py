from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FileField, TextAreaField, DateField, FloatField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, Length, NumberRange
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    phone_nr = StringField("Phone Number", validators=[Regexp(r'^0[1-9][0-9]{8}$', message="Invalid phone number.")])
    age = StringField("Age", validators=[Regexp(r'^[1-9][0-9]$')])
    user_type = SelectField("User Type", choices=[(0, "Student"), (1, "Instructor")], coerce=int)
    submit = SubmitField("Create account")


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


class CreateCourseForm(FlaskForm):
    name = StringField("Name of the Course", validators=[DataRequired()])
    instructor = SelectField("Instructor", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Course")


class AddStudentToCourseForm(FlaskForm):
    student = SelectField("Student", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Add Student to Course")


class UploadMaterialForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Length(max=500)])
    submit = SubmitField("Upload")


class AddAssignmentForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    text = TextAreaField("Description", validators=[DataRequired()])
    assignment_type = SelectField("Assignment Type", choices=[(0, "Upload File"), (1, "Solve Here")], coerce=int,  validators=[DataRequired()])
    deadline = DateField("Deadline", format="%Y-%m-%d", validators=[DataRequired()])
    file = FileField("Attachment (optional)")
    submit = SubmitField("Add Assignment")


class GradeSubmissionFormFile(FlaskForm):
    grade = FloatField("Grade", validators=[DataRequired(), NumberRange(min=0, max=10, message="Grade must be between 0 and 10.")])
    feedback = TextAreaField("Feedback (Optional)")
    file_link = StringField("Uploaded File", render_kw={"readonly": True})
    submit = SubmitField("Submit Grade")


class GradeSubmissionFormText(FlaskForm):
    grade = FloatField("Grade", validators=[DataRequired(), NumberRange(min=0, max=10, message="Grade must be between 0 and 10.")])
    feedback = TextAreaField("Feedback (Optional)")
    submission_content = TextAreaField("Student Submission", render_kw={"readonly": True})
    submit = SubmitField("Submit Grade")
