import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from database import (insert_owner_into_db, check_presence_in_db, verify_signin_with_db, retrieve_store_loc,
                      add_store_loc, retrieve_employees_data, add_employee_in_db, remove_employee, retrieve_products,
                      add_product_in_db, remove_product, get_items_in_stock, add_order_in_db, get_sales_report,
                      get_card_data)

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
    x_values_graph1, y_values_graph1 = get_items_in_stock(id)
    sales_table_values = get_sales_report(id)
    card_datas = get_card_data(id)

    return render_template('dashboard.html',
                           details={
                               'owner_id': id,
                               'name': name
                           },
                           graph_val={
                               'x_values_g1': x_values_graph1,
                               'y_values_g1': y_values_graph1
                           },
                           sales_report=sales_table_values,
                           card_data=card_datas)


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
    err_message = request.args.get('message')
    db = retrieve_employees_data(id)

    return render_template('employee_data.html',
                           details={'owner_id': id, 'name': name},
                           emp_data=db,
                           message=err_message)


@app.route("/<id>/<name>/issue_order/<product_img>")
def get_image(id, name, product_img):
    return send_from_directory('static/images/card_images', product_img)


@app.route("/<id>/<name>/issue-order")
def products_data(id, name):
    err_message = request.args.get('message')
    db = retrieve_products(id)

    return render_template('issue_order.html',
                           details={'owner_id': id, 'name': name},
                           product_data=db,
                           message=err_message)


@app.route("/<id>/<name>/place_order", methods=['POST'])
def place_order(id, name):
    data = request.json
    order_details = []
    data_val = data['quantities']

    for key in data_val:
        order_details.append({
            'prod_id': key,
            'prod_quantity': data_val[key]
        })

    customer_detail = data['customerDetails']

    status = add_order_in_db(id, order_details, customer_detail)

    if status == "done":
        return jsonify({"status": "success"})
    elif status == "stock":
        return jsonify({"status": "stock"})
    else:
        return jsonify({"status": "failed"})


@app.route("/<id>/<name>/add-product", methods=['POST'])
def add_products(id, name):
    data = request.form
    prod_name = data.get('prod-name')
    prod_price = data.get('prod-price')
    prod_quantity = data.get('prod-quantity')
    prod_img = data.get('prod-img')

    if not prod_name or not prod_price or not prod_quantity or not prod_img:
        return redirect(url_for('products_data',
                                id=id,
                                name=name,
                                message="None of the fields can be null"))

    else:
        status = add_product_in_db(id, prod_name, prod_price, prod_quantity, prod_img)

        if status:
            return redirect(url_for('products_data',
                                    id=id,
                                    name=name,
                                    message=None))
        else:
            return redirect(url_for('products_data',
                                    id=id,
                                    name=name,
                                    message="There was an error inserting new product details"))


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


@app.route("/<id>/<name>/add_employee", methods=['POST'])
def add_employee(id, name):
    data = request.form

    emp_name = data.get('emp-name')
    post = data.get('emp-post')
    salary = data.get('emp-salary')

    if not emp_name or not post or not salary:
        return redirect(url_for('employee_data',
                                id=id,
                                name=name,
                                message="Name/Post/Salary fields cannot be null"))

    else:
        status = add_employee_in_db(id, emp_name, post, salary)

        if status:
            return redirect(url_for('employee_data',
                                    id=id,
                                    name=name,
                                    message=None))
        else:
            return redirect(url_for('employee_data',
                                    id=id,
                                    name=name,
                                    message="There was an error inserting new employee details"))


@app.route("/<id>/<name>/delete_employee/<emp_id>", methods=['POST'])
def delete_employee(id, name, emp_id):
    status = remove_employee(emp_id, id)

    if status:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})


@app.route("/<id>/<name>/delete_product/<prod_id>", methods=['POST'])
def delete_product(id, name, prod_id):
    print("Triggered delete_product")
    status = remove_product(prod_id, id)

    if status:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})


if __name__ == "__main__":
    app.run(debug=True)
