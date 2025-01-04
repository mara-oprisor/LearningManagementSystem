from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import LoginForm
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

    account = relationship("UserAccount", back_populates="user", uselist=False)


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


@app.route("/home")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('log_in'))

    if current_user.status == "admin":
        return render_template("statistics.html", user=current_user)
    elif current_user.status == "instr":
        return render_template("home.html", user=current_user, navbar="header_instructor.html")
    elif current_user.status == "student":
        return render_template("home.html", user=current_user, navbar="header_student.html")
    else:
        abort(403)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
