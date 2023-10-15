# Store-Management-System

The Store Management System is a robust and user-friendly web application designed to simplify the complexities of managing a store's inventory, sales, and customer interactions. Built using Python's Flask framework and enhanced with Bootstrap for front-end design, it provides a one-stop solution for store owners to track and optimize their business operations. The application also leverages databases to store product details, customer data, and sales transactions, making it an all-inclusive platform for small to medium-sized businesses.

### Key Features:

**User Authentication**: Secure login and sign-up functionalities. \
**Inventory Management**: Real-time tracking of products. \
**Sales Analytics**: Dashboard featuring essential sales KPIs. \
**Order Management**: Seamless handling of customer orders. \
**Customer Database**: Keep track of customer information.

### Target Users:

* Small to medium business owners 
* Inventory managers 
* Sales analysts

### Tech Stack:

**Backend**: Python (Flask) \
**Frontend**: HTML, CSS (Bootstrap), JavaScript (jQuery, AJAX) \
**Data-Visualization**: ChartJs \
**Database**: SQLAlchemy, MySQL \
**Other Libraries**: bcrypt, python poetry

# Installation

### Prerequisites
* Python 3.x installed.
* MySQL Server up and running.

### 1. Clone Repo

```commandline
git clone https://github.com/shubh220922/Store-Management-System.git
cd store-management-system
```

### 2. Install Poetry

```commandline
pip install poetry
```

### 3. Activate Virtual Environment and Install Dependencies

```commandline
poetry install
poetry update
poetry shell
```

Note: create a `.env` file with the `DB_STRING` to connect to your own database


### 4. Run Application

```commandline
python server.py
```

# Database Schema

![img.png](img.png)

# Screenshots

### 1. Home Page
![img_2.png](img_2.png)

### 2. Sign Up and Sign In pages
Sign Up"
![img_3.png](img_3.png)
Sign In:
![img_4.png](img_4.png)

### 3. Dashboard feature
![img_5.png](img_5.png)

### 4. Outlet management feature
![img_1.png](img_1.png)

### 5. Employee management feature
![img_6.png](img_6.png)

and more......

