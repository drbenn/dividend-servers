from flask import Flask, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import random
import jsonify
import time
from datetime import datetime as dt
from datetime import time, timedelta
import schedule
import json
import threading # needed or else the sleep function on schedule will block all other code(ie, the server from running concurrently)
# finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
import multiprocessing
from urllib.request import urlopen
import calendar
import asyncio
import psycopg2
from psycopg2.extras import Json





app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

connection = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

grizzly_users_db_schema = {
   "username": 0,
   "email": 1,
   "password": 2,
   "join_date": 3
}

#cursor
cur = connection.cursor()


@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World! from Flask</p>"


@app.route("/json")
@cross_origin()
def json_test():
  pythonObject = [
    {
    "name": "billy",
    "age": 30,
    "city": "Chicago"
    },
            {
    "name": "willy",
    "age": 50,
    "city": "New York"
    }
  ]
  # converts to json
  json_value = json.dumps(pythonObject)
  return json_value

@app.route("/num")
def math():
    random_number = random.randrange(1,10000)
    return (f'<p>Hello! Your randomly assigned number was {random_number}. Strange right?!!?!?!?!?!?!?!?!?!?!?!!?</p>')


def db_fetch(query):
  cur = connection.cursor()
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  return retrieved_db_data

def register_error_handler(retrieved_db_data, submitted_username, submitted_email):
  # Check if username or password is unique
  db_username_index = 0
  db_email_index = 1
  error_message = None
  for user in retrieved_db_data:
    if user[db_username_index] == submitted_username:
      error_message = "Invalid request. Username already exists."
      print(error_message, 400)
      return error_message, 400
    if user[db_email_index] == submitted_email:
      error_message = "Invalid request. Email already exists."
      return error_message, 400
    
def register_new_user_in_db(username, email, password):
  cur = connection.cursor()
  cur.execute("INSERT INTO grizzly_users (username, email, password, join_date) values (%s, %s, %s, %s)", (username, email, password, dt.now() ))
  connection.commit()
  cur.close()
  return 'User registered successfully', 200

def authenticate_user(username, password):
  print("IN AUTHETICATE")
  retrieved_db_data = db_fetch(f"SELECT * from grizzly_users where username = '{username}' AND password = '{password}'")
  print(retrieved_db_data)
  print(len(retrieved_db_data))
  if len(retrieved_db_data) != 1:
    return False
  if len(retrieved_db_data) == 1:
    return True

def get_user_data(username):
  print("in get user data")
  retrieved_db_data = db_fetch(f"SELECT portfolios from grizzly_users where username = '{username}'")

@app.route("/register", methods=['POST'])
def register_user_handler() -> any:
  user_data = request.get_json()
  submitted_username = user_data["username"]
  submitted_email = user_data["email"]
  submitted_password = user_data["password"]
  retrieved_db_data = db_fetch(f"SELECT * from grizzly_users where username = '{submitted_username}' OR email = '{submitted_email}'")
  print(retrieved_db_data)
  if retrieved_db_data:
    return register_error_handler(retrieved_db_data, submitted_username, submitted_email)
  else:
    return register_new_user_in_db(submitted_username, submitted_email, submitted_password)

@app.route("/login", methods=['POST'])
def login_user_handler() -> any:  
  print("IN LOGIN")
  user_data = request.get_json()
  submitted_username = user_data["username"]
  submitted_password = user_data["password"]
  authenticate_result = authenticate_user(submitted_username, submitted_password)
  if not authenticate_result:
    print("AUTH FAILED")
    error_message = "Invalid request. Username or password incorrect."
    return error_message, 400
  if authenticate_result:
    print("AUTH SUCCESSFUL")
    # get_user_data(submitted_username)
    return 'User registered successfully', 200

  # retrieved_db_data = db_fetch(f"SELECT * from grizzly_users where username = '{submitted_username}' AND password = '{submitted_password}'")  
  
# @app.route("/login", methods=['GET'])
# def insert_new_user() -> any:
#   user_data = request.get_json()
#   submitted_username = user_data["username"]
#   submitted_email = user_data["email"]
#   submitted_password = user_data["password"]
#   # Check if username or password is unique
#   cur = connection.cursor()
#   query = "SELECT username, email FROM grizzly_users"
#   cur.execute(query)
#   retrieved_db_data = cur.fetchall()
#   is_username_and_password_unique = True
#   error_message = None
#   for user in retrieved_db_data:
#     db_username = user[grizzly_users_db_schema["username"]]
#     db_email = user[grizzly_users_db_schema["email"]]
#     if submitted_username == db_username:
#       print('username already in use')
#       is_username_and_password_unique = False
#       error_message = 'Invalid request. Username already exists.'
#     elif submitted_email == db_email:
#       print('email already in use')
#       is_username_and_password_unique = False
#       error_message = 'Invalid request. Email already exists.'

#   if is_username_and_password_unique:
#     cur = connection.cursor()
#     cur.execute("INSERT INTO grizzly_users (username, email, password, join_date) values (%s, %s, %s, %s)", (submitted_username, submitted_email, submitted_password, dt.now() ))
#     connection.commit()
#     cur.close()
#     return 'User registered successfully', 200
#   else:
#     cur.close()
#     return error_message, 400
  

if __name__ == "__main__": app.run()