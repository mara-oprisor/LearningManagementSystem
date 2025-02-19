from flask import Flask, render_template, redirect, url_for, flash, abort, request, send_file
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float, Boolean
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import *
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)

UPLOAD_COURSES_FOLDER = "static/uploads/courses"
app.config['UPLOAD_COURSES_FOLDER'] = UPLOAD_COURSES_FOLDER


# Create database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning-system.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class UserAccount(db.Model, UserMixin):
    __tablename__ = "user_account"
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    user = relationship("User", back_populates="account")


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    phone_number: Mapped[str] = mapped_column(String(10), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    account = relationship("UserAccount", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teaching_course = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")
    enrollment = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    grade = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")


class Course(db.Model):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    instructor_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))

    instructor = relationship("User", back_populates="teaching_course")
    enrollment = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    material = relationship("CourseMaterial", back_populates="course", cascade="all, delete-orphan")
    assignment = relationship("Assignments", back_populates="course", cascade="all, delete-orphan")
    grade = relationship("Grade", back_populates="course", cascade="all, delete-orphan")


class Enrollment(db.Model):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("course.id"))
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))

    course = relationship("Course", back_populates="enrollment")
    student = relationship("User", back_populates="enrollment")


class CourseMaterial(db.Model):
    __tablename__ = "course_material"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("course.id"))
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    course = relationship("Course", back_populates="material")


class Assignments(db.Model):
    __tablename__ = "assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("course.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(100), nullable=True)
    file_path: Mapped[str] = mapped_column(String(250), nullable=True)
    assignment_type: Mapped[int] = mapped_column(Integer, nullable=False)
    deadline: Mapped[str] = mapped_column(String(15), nullable=False)

    course = relationship("Course", back_populates="assignment")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="assignment")


class Grade(db.Model):
    __tablename__ = "grade"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    course_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("course.id"))
    assignment_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("assignments.id"))  # Link to Assignments table
    grade: Mapped[float] = mapped_column(Float, nullable=False)

    student = relationship("User", back_populates="grade")
    course = relationship("Course", back_populates="grade")
    assignment = relationship("Assignments", back_populates="grades")


class Submission(db.Model):
    __tablename__ = "submission"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("assignments.id"))
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    content: Mapped[str] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(100), nullable=True)
    file_path: Mapped[str] = mapped_column(String(250), nullable=True)
    is_graded: Mapped[bool] = mapped_column(Boolean, default=False)

    assignment = relationship("Assignments", back_populates="submissions")
    student = relationship("User", back_populates="submissions")


with app.app_context():
    db.create_all()


@app.route('/')
def welcome():
    return render_template("welcome.html")


@app.route('/login', methods=["GET", "POST"])
def log_in():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = db.session.execute(db.select(UserAccount).where(UserAccount.username == username))
        user_details = result.scalar()

        if not user_details:
            flash("Username does not exist. Please try again or register.", "error")
            return redirect(url_for('log_in'))
        elif user_details.password != password:
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for('log_in'))
        else:
            result_user = db.session.execute(db.select(User).where(User.id == user_details.user_id))
            user = result_user.scalar()
            login_user(user)

            if user.status == "admin":
                return redirect(url_for('home'))
            elif user.status == "instr":
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))

    return render_template("login.html", form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        name = form.name.data
        email = form.email.data
        phone_nr = form.phone_nr.data
        age = int(form.age.data) if form.age.data.isdigit() else None
        user_type = "student" if form.user_type.data == 0 else "instr"

        # Check if username or email already exists
        existing_username = db.session.execute(
            db.select(UserAccount).where(UserAccount.username == username)
        ).scalar()
        existing_email = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if existing_username:
            flash("Username already exists. Please choose a different username.", "error")
            return redirect(url_for('register'))
        if existing_email:
            flash("Email already exists. Please use a different email.", "error")
            return redirect(url_for('register'))

        new_user = User(
            name=name,
            email=email,
            phone_number=phone_nr,
            age=age,
            status=user_type
        )
        db.session.add(new_user)
        db.session.commit()

        new_account = UserAccount(
            user_id=new_user.id,
            username=username,
            password=password
        )
        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('log_in'))

    return render_template("register.html", form=form)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.status != "admin":
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function


def instructor_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.status != "instr":
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function


def student_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.status != "student":
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function


@app.route('/home')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('log_in'))

    if current_user.status == "admin":
        # Extract statistics
        total_students = db.session.execute(
            db.select(db.func.count()).where(User.status == "student")
        ).scalar()
        total_instructors = db.session.execute(
            db.select(db.func.count()).where(User.status == "instr")
        ).scalar()
        total_courses = db.session.execute(
            db.select(db.func.count()).select_from(Course)
        ).scalar()

        stats = {
            "students": total_students,
            "instructors": total_instructors,
            "courses": total_courses
        }

        return render_template("statistics.html", user=current_user, stats=stats)
    elif current_user.status == "instr":
        return render_template("home.html", user=current_user, navbar="header_instr.html")
    elif current_user.status == "student":
        return render_template("home.html", user=current_user, navbar="header_student.html")
    else:
        abort(403)


@app.route('/profile', methods=["GET", "POST"])
def profile():
    user = db.get_or_404(User, current_user.id)
    user_details = db.get_or_404(UserAccount, current_user.id)

    if not current_user.is_authenticated:
        abort(403)

    if current_user.status in ["student", "instr"]:
        form = ProfileForm(
            name=user.name,
            email=user.email,
            phone_nr=user.phone_number,
            age=user.age,
            username=user_details.username
        )

        if form.validate_on_submit():
            email_exists = db.session.execute(db.select(User).filter(User.email == form.email.data)).scalar()
            phone_exists = db.session.execute(db.select(User).filter(User.phone_number == form.phone_nr.data)).scalar()
            username_exists = db.session.execute(db.select(UserAccount).filter(UserAccount.username == form.username.data)).scalar()

            if email_exists and email_exists.id != user.id:
                form.email.errors.append("This email is already in use by another user.")
            elif phone_exists and phone_exists.id != user.id:
                form.phone_nr.errors.append("This phone number is already in use by another user.")
            elif username_exists and username_exists.user_id != user.id:
                form.username.errors.append("This username is already in use by another user.")
            else:
                user.name = form.name.data
                user.email = form.email.data
                user.phone_number = form.phone_nr.data
                user.age = form.age.data
                user_details.username = form.username.data

                db.session.commit()
                login_user(user)
                return redirect(url_for('profile'))

        return render_template(
            "profile.html",
            navbar=f"header_{current_user.status}.html",
            form=form,
            user=user,
            user_details=user_details
        )
    else:
        abort(403)


@app.route('/students')
@admin_only
def see_all_students():
    result = db.session.execute(db.select(User).where(User.status == "student"))
    students = result.scalars().all()
    return render_template(
        "people_list.html",
        list=students,
        title="Students"
    )


@app.route('/instructors')
@admin_only
def see_all_instructors():
    result = db.session.execute(db.select(User).where(User.status == "instr"))
    instructors = result.scalars().all()
    return render_template(
        "people_list.html",
        list=instructors,
        title="Instructors"
    )


@app.route('/change-password/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def change_password(user_id):
    user_details = db.get_or_404(UserAccount, user_id)
    user = db.get_or_404(User, user_id)
    form = ChangePasswordForm()

    if form.validate_on_submit():
        new_password = form.newPassword.data
        user_details.password = new_password

        db.session.commit()

        if user.status == "student":
            return redirect(url_for('see_all_students'))
        elif user.status == "instr":
            return redirect(url_for('see_all_instructors'))

    return render_template("change_password.html", form=form)


@app.route('/view-profile/<int:user_id>')
@admin_only
def view_profile(user_id):
    user = db.get_or_404(User, user_id)

    return render_template("view_profile.html", user=user)


@app.route('/delete_user/<int:user_id>')
@admin_only
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()

    if user.status == "student":
        return redirect(url_for('see_all_students'))
    elif user.status == "instr":
        return redirect(url_for('see_all_instructors'))


@app.route('/courses', methods=["GET", "POST"])
@admin_only
def courses():
    form = CreateCourseForm()

    result = db.session.execute(db.select(User).where(User.status == "instr")).scalars().all()
    instructors = [(instructor.id, instructor.name) for instructor in result]
    form.instructor.choices = instructors

    course_list = db.session.execute(db.select(Course)).scalars().all()

    if form.validate_on_submit():
        chosen_instructor = form.instructor.data
        course_name = form.name.data

        new_course = Course(name=course_name, instructor_id=chosen_instructor)
        db.session.add(new_course)
        db.session.commit()

        return redirect(url_for("courses"))

    return render_template("courses.html", form=form, list=course_list)


@app.route('/details_course/<int:course_id>')
@admin_only
def see_details_course(course_id):
    course = db.get_or_404(Course, course_id)

    result = db.session.execute(db.select(Enrollment).where(Enrollment.course_id == course_id)).scalars().all()
    students_id = [student.student_id for student in result]
    students = []
    for s_id in students_id:
        student = db.get_or_404(User, s_id)
        students.append(student)

    instructor = db.get_or_404(User, course.instructor_id)

    return render_template("see_details_course.html", title=course.name, students=students, instructor=instructor.name)


@app.route('/add_student_to_course/<int:course_id>', methods=["GET", "POST"])
@admin_only
def add_student_to_course(course_id):
    form = AddStudentToCourseForm()
    course = db.get_or_404(Course, course_id)

    enrolled_students_ids = db.session.execute(db.select(Enrollment.student_id).where(Enrollment.course_id == course_id)).scalars().all()
    available_students = db.session.execute(db.select(User).where(User.status == "student", User.id.not_in(enrolled_students_ids))).scalars().all()

    form.student.choices = [(student.id, student.name) for student in available_students]

    if form.validate_on_submit():
        chosen_student = form.student.data
        new_enrollment = Enrollment(course_id=course_id, student_id=chosen_student)
        db.session.add(new_enrollment)
        db.session.commit()

        return redirect(url_for("courses"))

    return render_template("add_student_to_course.html", form=form, title=course.name)


@app.route('/my_courses', methods=["GET"])
@student_only
def my_courses():
    if not current_user.is_authenticated:
        return redirect(url_for('log_in'))

    enrolled_courses = db.session.execute(
        db.select(Course).join(Enrollment).where(Enrollment.student_id == current_user.id)
    ).scalars().all()

    courses_data = []
    for course in enrolled_courses:
        materials = db.session.execute(
            db.select(CourseMaterial).where(CourseMaterial.course_id == course.id)
        ).scalars().all()

        assignments = db.session.execute(
            db.select(Assignments).where(Assignments.course_id == course.id)
        ).scalars().all()

        for assignment in assignments:
            submission = db.session.execute(
                db.select(Submission).where(
                    Submission.assignment_id == assignment.id,
                    Submission.student_id == current_user.id
                )
            ).scalar()
            assignment.is_done = submission is not None

        courses_data.append({
            "course": course,
            "materials": materials,
            "assignments": assignments
        })

    return render_template("my_courses.html", courses=courses_data)


@app.route('/solve_assignment/<int:assignment_id>', methods=["GET", "POST"])
@student_only
def solve_assignment(assignment_id):
    assignment = db.get_or_404(Assignments, assignment_id)

    if request.method == "POST":
        content = request.form.get("content")
        file = request.files.get("file")

        file_name = secure_filename(file.filename) if file else None
        file_path = None
        if file_name:
            upload_path = os.path.join(app.config['UPLOAD_COURSES_FOLDER'], str(assignment.course_id), "submissions")
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, file_name)
            file.save(file_path)

        new_submission = Submission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            content=content,
            file_name=file_name,
            file_path=file_path
        )
        db.session.add(new_submission)
        db.session.commit()

        return redirect(url_for('my_courses'))

    return render_template("solve_assignment.html", assignment=assignment)


@app.route('/upload_materials/<int:course_id>', methods=["GET", "POST"])
@instructor_only
def upload_course_material(course_id):
    form = UploadMaterialForm()
    course = db.get_or_404(Course, course_id)

    if form.validate_on_submit():
        file = form.file.data
        description = form.description.data

        file_name = secure_filename(file.filename)
        file_path = os.path.join("uploads/courses", str(course_id))
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, file_name)

        file.save(full_path)

        new_material = CourseMaterial(
            course_id=course_id,
            file_name=file_name,
            file_path=full_path,
            description=description
        )
        db.session.add(new_material)
        db.session.commit()

        return redirect(url_for('upload_course_material', course_id=course_id))

    return render_template(
        "upload_materials.html",
        form=form,
        course=course
    )


@app.route('/files/<int:course_id>/<filename>', methods=["GET"])
def serve_file(course_id, filename):
    filename = secure_filename(filename)

    directory = os.path.join(app.root_path, "uploads", "courses", str(course_id))
    file_path = os.path.join(directory, filename)

    if not os.path.exists(file_path):
        print("File does not exist.")
        abort(404)

    return send_file(file_path, as_attachment=True)


@app.route('/grades', methods=["GET"])
@student_only
def view_grades():
    if not current_user.is_authenticated:
        return redirect(url_for('log_in'))

    grades = db.session.execute(
        db.select(Grade)
        .join(Assignments)
        .join(Course)
        .where(Grade.student_id == current_user.id)
    ).scalars().all()

    grades_data = []
    for grade in grades:
        submission = db.session.execute(
            db.select(Submission)
            .where(
                Submission.assignment_id == grade.assignment_id,
                Submission.student_id == current_user.id
            )
        ).scalar()

        grades_data.append({
            "course_name": grade.course.name,
            "assignment_title": grade.assignment.title,
            "grade": grade.grade,
            "submission": {
                "content": submission.content if submission else None,
                "file_name": submission.file_name if submission else None,
                "file_path": submission.file_path if submission else None
            }
        })

    return render_template("grades.html", grades=grades_data)


@app.route('/taught_courses')
@instructor_only
def instructor_courses():
    course_list = db.session.execute(db.select(Course).where(Course.instructor_id == current_user.id)).scalars().all()

    courses_data = []
    for course in course_list:
        materials = db.session.execute(db.select(CourseMaterial).where(CourseMaterial.course_id == course.id)).scalars().all()

        assignments = db.session.execute(db.select(Assignments).where(Assignments.course_id == course.id)).scalars().all()

        courses_data.append({
            "course": course,
            "materials": materials,
            "assignments": assignments
        })

    return render_template("instructor_courses.html", courses=courses_data)


@app.route('/add_assignment/<int:course_id>', methods=["GET", "POST"])
@instructor_only
def add_assignment(course_id):
    course = db.get_or_404(Course, course_id)
    form = AddAssignmentForm()

    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        assignment_type = form.assignment_type.data
        deadline = form.deadline.data
        file = form.file.data

        file_name = secure_filename(file.filename) if file else None
        file_path = None
        if file_name:
            upload_path = os.path.join(app.config['UPLOAD_COURSES_FOLDER'], str(course_id), "assignments")
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, file_name)
            file.save(file_path)

        new_assignment = Assignments(
            course_id=course_id,
            title=title,
            text=text,
            assignment_type=assignment_type,
            deadline=deadline.strftime("%Y-%m-%d"),
            file_name=file_name,
            file_path=file_path
        )
        db.session.add(new_assignment)
        db.session.commit()

        return redirect(url_for('instructor_courses'))

    return render_template("add_assignment.html", course=course, form=form)


@app.route('/grade_assignments')
@instructor_only
def grade_assignments():
    if not current_user.is_authenticated:
        return redirect(url_for('log_in'))

    ungraded_submissions = db.session.execute(db.select(Submission).join(Assignments).join(Course).where(Course.instructor_id == current_user.id, Submission.is_graded == False)).scalars().all()

    return render_template("ungraded_assignments.html", submissions=ungraded_submissions)


@app.route('/grade_submission/<int:submission_id>', methods=["GET", "POST"])
@instructor_only
def grade_submission(submission_id):
    submission = db.get_or_404(Submission, submission_id)
    assignment = submission.assignment
    form = GradeSubmissionFormText()

    if assignment.assignment_type == 1:
        form.submission_content.data = submission.content
    elif assignment.assignment_type == 0:
        form = GradeSubmissionFormFile()
        if submission.file_name:
            file_url = url_for('static', filename=submission.file_path)
            form.file_link.data = f"Download file: {file_url}"

    if form.validate_on_submit():
        grade_value = form.grade.data
        feedback = form.feedback.data

        new_grade = Grade(
            student_id=submission.student_id,
            course_id=assignment.course_id,
            assignment_id=assignment.id,
            grade=grade_value
        )
        db.session.add(new_grade)

        if feedback:
            submission.feedback = feedback

        submission.is_graded = True
        db.session.commit()

        return redirect(url_for('grade_assignments'))

    return render_template("grade_submission.html", submission=submission, form=form)


@app.route('/logout', methods=["GET", "POST"])
def log_out():
    logout_user()
    return redirect(url_for('welcome'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
