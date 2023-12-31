from flask import Flask, request, jsonify
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

data_schema = {
  "ticker": 0,
  "name": 1,
  "type": 2,
  "industry": 3,
  "website": 4,
  "logo": 5,
  "dividend_yield": 6,
  "years_dividend_growth": 7, 
  "growth_all_years_of_history": 8, 
  "payout_ratios": 9,
  "three_year_cagr": 10, 
  "five_year_cagr": 11, 
  "year_price_high": 12,
  "year_price_low": 13,
  "beta": 14,
  "backup_stock_price": 15,
  "backup_stock_price_date_saved": 16,
  "dividend_payment_months_and_count": 17,
  "annual_dividend": 18
}

#cursor
cur = connection.cursor()


@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, Grizzly Server!</p>"


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
  # print("fetch returned")
  # print(retrieved_db_data)
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
  if len(tickers) > 1:
    db_query = ''
    for index, item in enumerate(tickers):
      if index == 0:
        db_query += f"ticker = '{item}'"
      else:
        db_query += f" OR ticker = '{item}'"
    return db_query
  else:
    return f"ticker = '{tickers[0]}'"

def data_transform_to_dict(data):
  data_dict_array = []
  for item in data:
    data_dict = {
    "ticker": item[data_schema["ticker"]],
    "name": item[data_schema["name"]],
    "type": item[data_schema["type"]],
    "industry": item[data_schema["industry"]],
    "website": item[data_schema["website"]],
    "logo": item[data_schema["logo"]],
    "dividend_yield": item[data_schema["dividend_yield"]],
    "years_dividend_growth": item[data_schema["years_dividend_growth"]], 
    "growth_all_years_of_history": item[data_schema["growth_all_years_of_history"]], 
    "payout_ratios": item[data_schema["payout_ratios"]],
    "three_year_cagr": item[data_schema["three_year_cagr"]], 
    "five_year_cagr": item[data_schema["five_year_cagr"]], 
    "year_price_high": item[data_schema["year_price_high"]],
    "year_price_low": item[data_schema["year_price_low"]],
    "beta": item[data_schema["beta"]],
    "backup_stock_price": item[data_schema["backup_stock_price"]],
    "backup_stock_price_date_saved": item[data_schema["backup_stock_price_date_saved"]],
    "dividend_payment_months_and_count": item[data_schema["dividend_payment_months_and_count"]],
    "annual_dividend": item[data_schema["annual_dividend"]]
    }
    data_dict_array.append(data_dict)
  return data_dict_array

@app.route("/dataquery", methods=["POST", "GET"])
def get_portfolio_tickers() -> any:
  tickers_submitted = request.get_json()
  print(f"tickers submitted: {tickers_submitted}")
  tickers_query = http_query_to_db_query_tickers(tickers_submitted)
  query =  f"SELECT ticker, name, equity_type, industry, website, logo, dividend_yield, years_dividend_growth, growth_all_years_of_history, payout_ratios, three_year_cagr, five_year_cagr, year_price_high, year_price_low, beta, backup_stock_price, backup_stock_price_date_saved, dividend_payment_months_and_count, annual_dividends from grizzly_stocks WHERE {tickers_query}"
  ticker_data = db_fetch(query)
  data_dict = data_transform_to_dict(ticker_data)
  return data_dict

@app.route("/searchtickers", methods=["GET"])
def get_search_tickers() -> any:
  query = "SELECT ticker, name from grizzly_stocks where has_dividend = 'true' AND industry IS NOT NULL AND dividend_yield IS NOT NULL AND years_dividend_growth IS NOT NULL AND payout_ratios IS NOT NULL AND three_year_cagr IS NOT NULL  AND five_year_cagr IS NOT NULL AND annual_dividends IS NOT NULL"
  ticker_data = db_fetch(query)
  return ticker_data

  

if __name__ == "__main__": app.run()