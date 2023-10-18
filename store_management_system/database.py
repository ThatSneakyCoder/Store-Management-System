import os
from datetime import datetime
import random

import bcrypt

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, select, ForeignKey, Float, and_
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


load_dotenv()
Base = declarative_base()


class Owners(Base):
    __tablename__ = "owners"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50), nullable=False)
    email = Column("email", String(100), nullable=False, unique=True)
    password = Column("password", String(100), nullable=False)
    outlets = relationship('Outlets', back_populates='owner')
    employee = relationship('Employees', back_populates='owner')
    orders = relationship('Orders', back_populates='owner')
    customers = relationship('Customers', back_populates='owner')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"Name: {self.name}\n email: {self.email}"


class Outlets(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'))
    owner = relationship('Owners', back_populates='outlets')

    def __repr__(self):
        return f"<Outlet(outlet_id={self.outlet_id}, lat={self.lat}, lng={self.lng}, owner_id={self.owner_id})>"


class Employees(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    post = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'))
    owner = relationship('Owners', back_populates='employee')

    def __repr__(self):
        return f"<Employee(employee_id={self.id}, name={self.name}, post={self.post}, salary={self.salary})>"


class Products(Base):
    __tablename__ = "products"

    owner_id = Column(Integer, ForeignKey('owners.id'))
    prod_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_name = Column(String(100), nullable=False)
    prod_price = Column(Integer, nullable=False)
    prod_quantity = Column(Integer, nullable=False)
    prod_image = Column(String(500), nullable=False)
    orders = relationship('Orders', back_populates='product')

    def __repr__(self):
        return f"Products(owner_id={self.owner_id}, prod_id={self.prod_id}, prod_name={self.prod_name}, prod_price={self.prod_price}, prod_quantity={self.prod_quantity}, prod_image={self.prod_image})"


class Orders(Base):
    __tablename__ = "orders"

    order_val = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=False)
    prod_id = Column(Integer, ForeignKey('products.prod_id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False)
    sold_prod_quantity = Column(Integer, nullable=False)

    # Relationships
    product = relationship('Products', back_populates='orders')
    owner = relationship('Owners', back_populates='orders')

    def __repr__(self):
        return (f"Orders(order_id={self.order_id}, "
                f"prod_id={self.prod_id}, "
                f"owner_id={self.owner_id}, "
                f"sold_prod_quantity={self.sold_prod_quantity}")


class Customers(Base):
    __tablename__ = "customers"

    owner_id = Column(Integer, ForeignKey('owners.id'))
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_address = Column(String(500), nullable=False)
    customer_city = Column(String(100), nullable=False)
    customer_state = Column(String(100), nullable=False)
    customer_zip = Column(Integer, nullable=False)
    owner = relationship('Owners', back_populates='customers')

    def __repr__(self):
        return (f"Customers(customer_id={self.customer_id}, "
                f"customer_name={self.customer_name}, "
                f"customer_email={self.customer_email}, "
                f"customer_address={self.customer_address}, "
                f"customer_city={self.customer_city}, "
                f"customer_state={self.customer_state}, "
                f"customer_zip={self.customer_zip})")

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'default_db_name')

db_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(db_string, echo=True)

Session = sessionmaker(bind=engine)
session = Session()  # we can do all sort of things with this now
Base.metadata.create_all(bind=engine)  # takes all the classes and creates their database


def get_sales_report(owner_id):
    result = []

    query_orders = session.query(Orders.order_id).filter(Orders.owner_id == owner_id).distinct().all()

    for index, order in enumerate(query_orders, start=1):

        query_products = session.query(Orders.prod_id).filter(Orders.order_id == order.order_id).all()
        product_list = [prod.prod_id for prod in query_products]

        total_sales = 0

        for prod in product_list:
            query_price = session.query(Products.prod_price).filter(Products.prod_id == prod).one()
            total_sales += query_price[0]

        result.append({
            'order_number': index,
            'order_id': order.order_id,
            'product_list': product_list,
            'total_sales': total_sales,
        })

    return result


def add_order_in_db(prod_owner_id, order_details, customer_details):
    try:
        status = ""
        order_id = int(datetime.now().strftime('%H%M%S') + str(random.randint(0, 10)))

        for order in order_details:
            # inserting into the db
            new_order = Orders(order_id=order_id,
                               prod_id=order['prod_id'],
                               owner_id=prod_owner_id,
                               sold_prod_quantity=order['prod_quantity'])

            # reducing quantity from the available stock
            product = session.query(Products).filter_by(prod_id=order['prod_id']).first()

            if product and product.prod_quantity >= int(order['prod_quantity']):
                product.prod_quantity -= int(order['prod_quantity'])
            else:
                product.prod_quantity += 100
                product.prod_quantity -= int(order['prod_quantity'])
                status += "stock"

            session.add(new_order)

        new_customer = Customers(
            owner_id=prod_owner_id,
            customer_name=customer_details['name'],
            customer_email=customer_details['email'],
            customer_address=customer_details['address'],
            customer_city=customer_details['city'],
            customer_state=customer_details['state'],
            customer_zip=customer_details['zip']
        )

        session.add(new_customer)

        session.commit()
        if status:
            return status
        else:
            return "done"
    except IntegrityError:
        session.rollback()
        print("\033[91mIntegrityError: Error while inserting new order details\033[0m")
        return "failed"
    except SQLAlchemyError:
        session.rollback()
        print("\033[91mSQLAlchemyError: Could not insert order details\033[0m")
        return "failed"


def get_card_data(owner_id):
    result = {}

    count_products = session.query(Products).filter(Products.owner_id == owner_id).count()
    count_customers = session.query(Customers).filter(Customers.owner_id == owner_id).count()
    query_orders = session.query(Orders.order_id).filter(Orders.owner_id == owner_id).distinct().all()

    total_sales = 0

    for index, order in enumerate(query_orders, start=1):

        query_products = session.query(Orders.prod_id).filter(Orders.order_id == order.order_id).all()
        product_list = [prod.prod_id for prod in query_products]

        for prod in product_list:
            query_price = session.query(Products.prod_price).filter(Products.prod_id == prod).one()
            total_sales += query_price[0]

    return {
        'count_products': count_products,
        'count_customers': count_customers,
        'total_sales': total_sales
    }

def add_product_in_db(prod_owner_id, prod_name, prod_price, prod_quantity, prod_img):
    try:
        new_prod = Products(owner_id=prod_owner_id,
                            prod_name=prod_name,
                            prod_price=prod_price,
                            prod_quantity=prod_quantity,
                            prod_image=prod_img)
        session.add(new_prod)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mError while inserting new product details\033[0m")
        return False


def retrieve_products(owner_id):
    try:
        all_prods = session.query(Products).filter(Products.owner_id == owner_id).all()
        response = []

        for prod in all_prods:
            response.append({
                'prod_id': prod.prod_id,
                'prod_name': prod.prod_name,
                'prod_price': prod.prod_price,
                'prod_quantity': prod.prod_quantity,
                'prod_image': prod.prod_image,
            })

        return response
    except IntegrityError:
        session.rollback()
        print("\033[91mIntegrityError: Something went wrong\033[0m")
        return False
    except SQLAlchemyError:
        session.rollback()
        print("\033[91mSQLAlchemyError: Something went wrong\033[0m")
        return False


def insert_owner_into_db(details):
    user_name = details['name']
    user_email = details['email']
    user_password = details['password'].encode('utf-8')
    hashed_user_password = bcrypt.hashpw(user_password, bcrypt.gensalt())

    try:
        new_owner = Owners(name=user_name, email=user_email, password=hashed_user_password)
        session.add(new_owner)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mEmail already exists\033[0m")
        return False


def check_presence_in_db(details):
    user_email = details['email']

    get_owner = select(Owners).where(Owners.email == user_email)
    result = session.execute(get_owner).fetchone()
    return bool(result)


def verify_signin_with_db(details):
    user_email = details['email']
    user_password = details['password'].encode('utf-8')
    get_details_of_owner_with_email = select(Owners).where(Owners.email == user_email)
    result = session.execute(get_details_of_owner_with_email).fetchone()

    if result is not None:
        password = result[0].password.encode('utf-8')
        if bcrypt.checkpw(user_password, password):
            row = result[0]
            name = row.name
            id = row.id
            return id, name

    return None


def retrieve_store_loc(owner_id):
    try:
        get_store_list = (session
                          .query(Outlets)
                          .filter(Outlets.owner_id == owner_id)
                          .all())
        response = []

        for store in get_store_list:
            response.append({
                'lat': store.lat,
                'lng': store.lng
            })
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def add_store_loc(store_owner_id, store_lat, store_lng):
    try:
        new_loc = Outlets(lat=store_lat,
                          lng=store_lng,
                          owner_id=store_owner_id)
        session.add(new_loc)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mError while inserting store location\033[0m")
        return False


def retrieve_employees_data(owner_id):
    try:
        get_employee_list = (session
                             .query(Employees)
                             .filter(Employees.owner_id == owner_id)
                             .all())
        response = []

        for employee in get_employee_list:
            response.append({
                'id': employee.id,
                'name': employee.name,
                'post': employee.post,
                'salary': employee.salary
            })

        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def add_employee_in_db(employee_owner_id, employee_name, employee_post, employee_salary):
    try:
        new_employee = Employees(name=employee_name,
                                 post=employee_post,
                                 salary=employee_salary,
                                 owner_id=employee_owner_id)
        session.add(new_employee)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mError while inserting new employee details\033[0m")
        return False


def remove_employee(id, owner_id):
    try:
        session.query(Employees).filter(and_(Employees.id == id, Employees.owner_id == owner_id)).delete()
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mCould not delete entry due to Integrity Error\033[0m")
        return False
    except SQLAlchemyError:
        session.rollback()
        print("\033[91mCould not delete entry due to Database Error\033[0m")
        return False


def remove_product(prod_id, owner_id):
    try:
        print("Triggered remove_product")
        session.query(Products).filter(and_(Products.prod_id == prod_id, Products.owner_id == owner_id)).delete()
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mCould not delete entry due to Integrity Error\033[0m")
        return False
    except SQLAlchemyError:
        session.rollback()
        print("\033[91mCould not delete entry due to Database Error\033[0m")
        return False


def get_items_in_stock(owner_id):
    detail_of_items_in_stock = session.query(Products.prod_name).filter(Products.owner_id == owner_id).all()
    list_items_in_stock = []

    for prod_name in detail_of_items_in_stock:
        list_items_in_stock.append(prod_name[0])

    amount_of_items_in_stock = session.query(Products.prod_quantity).filter(Products.owner_id == owner_id).all()
    list_quantity_of_items = []

    for prod_quantity in amount_of_items_in_stock:
        list_quantity_of_items.append(prod_quantity[0])

    return list_items_in_stock, list_quantity_of_items
