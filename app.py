from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template("welcome.html")


@app.route('/login')
def log_in():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True, port=5003)
