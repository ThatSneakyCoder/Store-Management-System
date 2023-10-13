import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import insert_owner_into_db, check_presence_in_db, verify_signin_with_db, retrieve_store_loc, add_store_loc

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
    user_id, user_name = verify_signin_with_db(data)
    if user_id is not None:
        return redirect(url_for('user_dashboard', id=user_id, name=user_name))
    else:
        return render_template('user_does_not_exist.html')


@app.route("/<id>/<name>/dashboard")
def user_dashboard(id, name):
    return render_template('dashboard.html', details={'owner_id': id, 'name': name})


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


@app.route("/<id>/<name>/outlet")
def outlet(id, name):

    return render_template('outlet.html',
                           details={'owner_id': id, 'name': name})


@app.route("/<id>/<name>/employee-data")
def employee_data(id, name):
    db = [
        {
            'id': 1,
            'name': "kashyap",
            'post': "receptionist",
            'salary': 1200
        },
        {
            'id': 2,
            'name': "ashwin",
            'post': "janitor",
            'salary': 800
        }
    ]

    return render_template('employee_data.html',
                           details={'owner_id': id, 'name': name},
                           emp_data=db)


@app.route("/<id>/<name>/issue-order")
def issue_order(id, name):
    db = [
        {
            'order_id': 1,
            'products': [{
                             'prod_id': 1,
                             'prod_name': "Shaving cream"
                         },
                         {
                             'prod_id': 2,
                             'prod_name': "Detergent"
                         },
                         {
                             'prod_id': 3,
                             'prod_name': "Vegetable oil"
                         }]
        }
    ]

    return render_template('issue_order.html',
                           details={'owner_id': id, 'name': name},
                           order_data=db)


@app.route("/get_coordinates/<owner_id>")
def get_coordinates(owner_id):
    coords = retrieve_store_loc(owner_id)

    print(coords)

    if coords is not None:
        return jsonify({
            "owner_id": owner_id,
            "coordinates": coords
        })
    else:
        return jsonify([])


@app.route("/<id>/<name>/add_loc", methods=['POST'])
def add_loc(id, name):
    data = request.form

    lat = data.get('latitude')
    lng = data.get('longitude')

    if not lat or not lng:
        return render_template('outlet.html',
                               details={'owner_id': id, 'name': name},
                               message="Latitude and Longitude fields cannot be null")
    else:
        status = add_store_loc(id, lat, lng)

        if status:
            return render_template('outlet.html',
                                   details={'owner_id': id, 'name': name})
        else:
            return render_template('outlet.html',
                                   details={'owner_id': id, 'name': name},
                                   message="There was an error inserting the store location")


if __name__ == "__main__":
    app.run(debug=True)
