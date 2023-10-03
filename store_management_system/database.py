import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


connection = mysql.connector.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")
)


def insert_owner_into_db(details):
    query = (f"INSERT INTO owners "
             f"(name, email, password)"
             f"VALUES ('{details['name']}', '{details['email']}', '{details['password']}')")
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()


def check_presence_in_db(details):
    query = (f"SELECT COUNT(*) "
             f"FROM owners "
             f"WHERE email = '{details['email']}'")
    cursor = connection.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]

    if count > 0:
        return True
    else:
        return False


def verify_signin_with_db(details):
    query = (f"SELECT COUNT(*), name "
             f"FROM owners "
             f"WHERE email = '{details['email']}' AND password = '{details['password']}'")
    cursor = connection.cursor()
    cursor.execute(query)
    count, name = cursor.fetchone()

    if count == 1:
        return name
    else:
        return None


# if __name__ == '__main__':
#     details = {
#         'id': 1,
#         'email': 'sam@altman.com'
#     }
#     print(check_presence_in_db(details))
