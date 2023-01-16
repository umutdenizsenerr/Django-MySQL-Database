# University-Registration-System

This project utilizes the power of Django and MySQL to create a robust and user-friendly database management system. The project uses the Django framework to create a web application with a user interface, and interacts with a MySQL database to perform queries and manage data.

## Requirements

- MySQL
- Python(>3.8) and pip module.

## Getting Started

1. Clone or download this repository.
2. Install the required dependencies by running the following command: 
```
pip install -r requirements.txt
```
3. Create an .env file in the src folder (folder with the settings.py file) and insert the following information:
```
MYSQL_DATABASE=<YOUR_DB_NAME>
MYSQL_USER=<YOUR_USERNAME>
MYSQL_ROOT_PASSWORD=<YOUR_PASSWORD>
MYSQL_PASSWORD=<YOUR_PASSWORD>
MYSQL_HOST="localhost"
```
4. Make sure your MySQL server is up and running. Then, navigate to the project3 directory and run the following commands to set up the database according to the Django configurations:
```
cd project3
python3 manage.py makemigrations
python3 manage.py migrate
```

5. Run the following command to create and fill relevant tables:
```
python3 src/create_db.py
```
6. Finally, run the following command to start the development server:
```
python3 manage.py runserver
```
The website will be accessible at [http://127.0.0.1:8000/forum/](http://127.0.0.1:8000/forum/)

## Built With

- Django
- MySQL
- Python

## Authors
- Umut Deniz Şener
