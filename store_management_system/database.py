import os
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

    def __repr__(self):
        return f"Products(owner_id={self.owner_id}, prod_id={self.prod_id}, prod_name={self.prod_name}, prod_price={self.prod_price}, prod_quantity={self.prod_quantity}, prod_image={self.prod_image})"


engine = create_engine(os.getenv("DB_STRING"), echo=True)

Session = sessionmaker(bind=engine)
session = Session()  # we can do all sort of things with this now
Base.metadata.create_all(bind=engine)  # takes all the classes and creates their database


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


# def get_items_with_most_sales(owner_id):

