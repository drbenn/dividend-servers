from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import random
import time
from datetime import time, timedelta, datetime
import schedule
import json
import finnhub
import helper
from api_keys import FINNHUB_API_KEY, FMP_API_KEY
import threading # needed or else the sleep function on schedule will block all other code(ie, the server from running concurrently)
# finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
import multiprocessing
from urllib.request import urlopen

# print(finnhub_client.stock_symbols('US'))

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)




@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World! from Flask</p>"


@app.route("/interval")
@cross_origin()
def scheduled_activity():
    print(datetime.datetime.now())

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

@app.route("/getstocklistfromapi")
@cross_origin()
def get_stock_list():
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    # print(finnhub_client.stock_symbols('US'))
    json_value = json.dumps(finnhub_client.stock_symbols('US'))
    return json_value


@app.route("/num")
def math():
    random_number = random.randrange(1,10000)
    return (f'<p>Hello! Your randomly assigned number was {random_number}. Strange right?!!?!?!?!?!?!?!?!?!?!?!!?</p>')


@app.route("/dbtest")
def db_access():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    fetchdata = cur.fetchall()
    cur.close()

    return "logging data"

# def show_name():
#     print('at time...', helper.get_time())
#     print("Jerk")
#     print("bungole")


# schedule.every(2).seconds.do(show_name) # no threading & blocks api from running
# # schedule.every().day.at("18:30").do(show_name) # no threading & blocks api from running

# while True:
#     schedule.run_pending()
#     time.sleep(1)


# Update script must
# 1. get list of all stocks listed
# 2. get list of stock data from db
# 3. compare api list against db list
#    3.a. if no detail data is in db, grab data from api
#    3.b. if all stocks have detail data, loop through last updated time for stock and update(or based on dividend release date)
# def get_and_loop_data():
#     finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
#     # print(finnhub_client.stock_symbols('US'))
#     api_response = finnhub_client.stock_symbols('US')
#     # api_response = finnhub_client.symbol_lookup('apple')
#     quote_response = finnhub_client.quote('AAPL')
#     # print(api_response)
#     # api_response_as_json_string = json.dumps(finnhub_client.stock_symbols('US'), indent=2) #json.dumps converts python object to JSON string
#     # print(api_json_response)

#     i = 0
#     for item in api_response:
#         while i < 10:
#             print(item)
#             i += 1


# get_and_loop_data()


# def get_current_stock_price(symbol):
#   finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
#   quote_response = finnhub_client.quote(symbol)
#   current_price = quote_response["c"]
#   percent_change = quote_response["dp"]
#   previous_close = quote_response["pc"]
#   print(quote_response, current_price, percent_change, previous_close)
#   print('current price: ', current_price, 'percent change: ', percent_change, 'previous close: ', previous_close, 'as of...', helper.get_time())


# get_current_stock_price("AApl")




# def get_historical_dividends(symbol):
#     url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{symbol}?apikey={FMP_API_KEY}"
#     """
#     Receive the content of ``url``, parse it as JSON and return the object.

#     Parameters
#     ----------
#     url : str

#     Returns
#     -------
#     dict
#     """
#     response = urlopen(url)
#     data = response.read().decode("utf-8")
#     print(json.loads(data))
#     return json.loads(data)

# get_historical_dividends('msft')

def calculate_dividend_yield(sum_of_last_four_dividends, current_price):
    # dividend yield = annual dividend by current share price
    return (sum_of_last_four_dividends / current_price)

def calculate_x_year_cagr(ending_balance, beginning_balance, years):
    cagr = ((ending_balance / beginning_balance) ** ( 1 / years ))  - 1
    print(cagr)

calculate_x_year_cagr(2.54,1.59,5) # verified against MSFT Payouts of: $2.54 in 2022 vs $1.59 in 2017, 2022 - 2017 = 5 years for 0.09821 5yr CAGR

def calculate_dividend_payout_ratio(net_income, dividends_paid):
    dividend_payout_ratio = (dividends_paid / net_income)
    # print(dividend_payout_ratio)

#finanancials as reported

def get_quarterly_financials(symbol): # only reports quarters 1,2,3. Require EOY for quarter 4
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    response = finnhub_client.financials_reported(symbol=symbol, freq='quarterly')
    # print(response)
    print(len(response["data"]))
    for item in response["data"]:
        newest_quarter = None
        year = item["year"]
        quarter = item["quarter"]
        startDate = item["startDate"]
        endDate = item["endDate"]
        income_statement = item["report"]["ic"]

        for point in income_statement:
            if (point["label"] == "Net loss" and newest_quarter != F"{quarter} - {year}"):
                print("Net Loss Value: ", point["value"])
                print("net loss found")
                newest_quarter = F"{quarter} - {year}"
                break
            if (point["label"] == "Net income" and newest_quarter != F"{quarter} - {year}"):
                print("Net income Value: ", point["value"])
                print("net income found")
                newest_quarter = F"{quarter} - {year}"
        print(f"YEAR: {year} ---------------- QUARTER: {quarter}")

get_quarterly_financials("tsla")

if __name__ == "__main__": app.run()

