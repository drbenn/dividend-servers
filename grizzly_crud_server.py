from flask import Flask, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import random
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


@app.route("/register", methods=['POST'])
def insert_new_user() -> any:
  user_data = request.get_json()
  # for ticker in tickers_to_add_to_db:
  #    for ticker_info in all_current_us_tickers:
  #       if ticker == ticker_info["symbol"]: 
  print("USER REGISTER DATA")
  print(user_data)
  cur = connection.cursor()
  cur.execute("INSERT INTO grizzly_users (username, email, password, join_date) values (%s, %s, %s, %s)", (user_data["username"], user_data["email"], user_data["password"], dt.now() ))
  connection.commit()
  cur.close()
  return 'User registered successfully', 200

if __name__ == "__main__": app.run()