import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, select, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError
import bcrypt


load_dotenv()
Base = declarative_base()


class Owners(Base):
    __tablename__ = "owners"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50), nullable=False)
    email = Column("email", String(100), nullable=False, unique=True)
    password = Column("password", String(100), nullable=False)
    outlets = relationship('Outlets', back_populates='owner')

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


engine = create_engine(os.getenv("DB_STRING"), echo=True)

Session = sessionmaker(bind=engine)
session = Session()  # we can do all sort of things with this now
Base.metadata.create_all(bind=engine)  # takes all the classes and creates their database


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
        get_store_list = session.query(Outlets).filter(Outlets.owner_id == owner_id).all()
        session.flush()
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
        new_loc = Outlets(lat=store_lat, lng=store_lng, owner_id=store_owner_id)
        session.add(new_loc)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        print("\033[91mError while inserting store location\033[0m")
        return False


def get_employees(owner_id):
    try:
        get_employee_list = session.query(employee).all()
        session.flush()
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
