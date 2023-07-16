from flask import Flask, request, jsonify
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
from decimal import Decimal





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
  print("IN DB FETCH")
  cur = connection.cursor()
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  print("fetch returned")
  print(retrieved_db_data)
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
  

def http_query_to_db_query_tickers(tickers):
  print("in query_to_array")
  if len(tickers) > 1:
    print(tickers)
    db_query = ''
    for index, item in enumerate(tickers):
      if index == 0:
        db_query += f"ticker = '{item}'"
      else:
        db_query += f" OR ticker = '{item}'"
    print(f"db QUERY = {db_query}")
    return db_query
  else:
    return f"ticker = '{tickers[0]}'"


# @app.route("/portfoliodata", methods=["POST", "GET"])
@app.route("/dataquery", methods=["POST", "GET"])
def get_portfolio_tickers() -> any:
  tickers_submitted = request.get_json()
  print(f"tickers submitted: {tickers_submitted}")
  tickers_query = http_query_to_db_query_tickers(tickers_submitted)
  # query =  f"SELECT ticker, name, equity_type, industry, website, logo, dividend_yield from grizzly_stocks WHERE {tickers}"
  query =  f"SELECT ticker, name, equity_type, industry, website, logo, dividend_yield, years_dividend_growth, growth_all_years_of_history, payout_ratios, three_year_cagr, five_year_cagr, year_price_high, year_price_low, beta, backup_stock_price, backup_stock_price_date_saved, dividend_payment_months_and_count, annual_dividends from grizzly_stocks WHERE {tickers_query}"
  ticker_data = db_fetch(query)
  return ticker_data

  

if __name__ == "__main__": app.run()