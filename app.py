from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import LoginForm, ProfileForm, ChangePasswordForm
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)


# Create database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning-system.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Configure tables for the database
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
        return render_template("statistics.html", user=current_user)
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


@app.route('/logout', methods=["GET", "POST"])
def log_out():
    logout_user()
    return redirect(url_for('welcome'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
