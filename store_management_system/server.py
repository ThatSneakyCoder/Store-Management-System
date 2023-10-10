import os
from flask import Flask, render_template, request, redirect, url_for
from database import insert_owner_into_db, check_presence_in_db, verify_signin_with_db

current_directory = os.path.dirname(os.path.abspath(__file__))

static_folder_path = os.path.join(current_directory, 'static')
template_folder_path = os.path.join(current_directory, 'templates')

app = Flask(__name__, static_folder=static_folder_path, template_folder=template_folder_path)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/signup")
def sign_up():
    return render_template('signup.html')


@app.route("/signin")
def sign_in():
    return render_template('signin.html')


@app.route("/verify_signin", methods=['POST'])
def verify_signin():
    data = request.form
    user_name = verify_signin_with_db(data)
    if user_name is not None:
        return redirect(url_for('user_dashboard', name=user_name))
    else:
        return render_template('user_does_not_exist.html')


@app.route("/<name>/dashboard")
def user_dashboard(name):
    return render_template('dashboard.html', details={'name': name})


@app.route("/signup/successful", methods=['POST'])
def signup_successful():
    data = request.form
    is_present = check_presence_in_db(data)
    if is_present:
        return render_template('user_already_present.html')
    else:
        checker = insert_owner_into_db(data)
        if not checker:
            return "<h1>User already exists</h1>"
        return render_template('signup_successful.html',
                               signup_details=data)


if __name__ == "__main__":
    app.run(debug=True)
