from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import random
import time
from datetime import datetime as dt
from datetime import time, timedelta
import schedule
import json
import finnhub
import helper
from grizzly_db_builder.api_keys import FINNHUB_API_KEY, FMP_API_KEY
import threading # needed or else the sleep function on schedule will block all other code(ie, the server from running concurrently)
# finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
import multiprocessing
from urllib.request import urlopen
import calendar
import asyncio
import psycopg2
import finnhub
from psycopg2.extras import Json


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
    print(dt.datetime.now())

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



def calculate_dividend_yield(sum_of_last_four_dividends, current_price):
    # Get current price from finnhub api
    # Get last four dividends from db sourced from fmp api

    # dividend yield = annual dividend by current share price
    return (sum_of_last_four_dividends / current_price)

def get_basic_financials(symbol):
    # Store in DB - Up to minute not required
    # provides current ratio, sales/share,netMargin, beta AND 52 week hi/low
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    basic_financials = finnhub_client.company_basic_financials(symbol, 'all')
    return basic_financials


def calculate_x_year_cagr(ending_balance, beginning_balance, years):
    cagr = ((ending_balance / beginning_balance) ** ( 1 / years ))  - 1
    print(cagr)

calculate_x_year_cagr(2.54,1.59,5) # verified against MSFT total dividend/share payouts of: $2.54 in 2022 vs $1.59 in 2017, 2022 - 2017 = 5 years for 0.09821 5yr CAGR

def calculate_dividend_payout_ratio(net_income, dividends_paid):
    dividend_payout_ratio = (dividends_paid / net_income)
    # print(dividend_payout_ratio)

#finanancials as reported

def get_quarterly_financials(symbol): # only reports quarters 1,2,3. Require EOY for quarter 4
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    response = finnhub_client.financials_reported(symbol=symbol, freq='quarterly')
    # print(response)
    # print(len(response["data"]))
    for item in response["data"]:
        newest_quarter = None
        year = item["year"]
        quarter = item["quarter"]
        startDate = item["startDate"]
        endDate = item["endDate"]
        income_statement = item["report"]["ic"]

        for point in income_statement:
            if (point["label"] == "Net loss" and newest_quarter != F"{quarter} - {year}"):
                # print("Net Loss Value: ", point["value"])
                # print("net loss found")
                newest_quarter = F"{quarter} - {year}"
                break
            if (point["label"] == "Net income" and newest_quarter != F"{quarter} - {year}"):
                # print("Net income Value: ", point["value"])
                # print("net income found")
                newest_quarter = F"{quarter} - {year}"
        # print(f"YEAR: {year} ---------------- QUARTER: {quarter}")


def get_annual_financials(symbol):
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    # response = finnhub_client.financials_reported(symbol=symbol, freq='annual', to='2022')
    response = finnhub_client.financials_reported(symbol=symbol, freq='annual')
    # print(response)
    return response



# TODO - if net loss negative just return any value w/o referencing label
def get_net_income_loss_from_annual_financials(annual_financials) -> float:
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
        if item["concept"] == "us-gaap_NetIncomeLoss" and item["label"] == "Net income":
            net_income = item["value"]
            # print("NET INCOME")
            # print(net_income)
            return float(net_income)
        if item["concept"] == "us-gaap_NetIncomeLoss" and item["label"] == "Net loss":
            net_loss = item["value"]
            # print("NET LOSS")
            # print(net_loss)
            return float(net_loss)

def get_shares_outstanding_from_annual_financials(annual_financials):
    # print("in get shares outstanding")
    income_statement = annual_financials["data"][0]["report"]["ic"]
    # print(income_statement)
    for item in income_statement:
        # print(item)
        if item["concept"] == "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding" or item["concept"] == "WeightedAverageNumberOfDilutedSharesOutstanding":
            diluted_shares_outstanding = item["value"]
            # print("OUSTANDING SHARES")
            # print(diluted_shares_outstanding)
            return float(diluted_shares_outstanding)
        
def get_annual_common_stock_total_dividend_paid(annual_financials):
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
        if item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock":
            total_dividends_paid = item["value"]
            return float(total_dividends_paid)

def get_annualized_dividend_per_share(shares_outstanding, total_annual_dividends_paid):
    # print(f"shares: {shares_outstanding}")
    # print(f"divs paid: {total_annual_dividends_paid}")
    return float(total_annual_dividends_paid / shares_outstanding)

def get_historical_dividends(symbol):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{symbol}?apikey={FMP_API_KEY}"
    """
    Receive the content of ``url``, parse it as JSON and return the object.
    Parameters
    ----------
    url : str
    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    # print(json.loads(data))
    return json.loads(data)

def get_ttm_dividend_per_share_count_and_months(shares_outstanding, historical_dividends):
    latest_dividend = historical_dividends["historical"][0]
    latest_ex_dividend_date = latest_dividend["date"]
    # latest_payment_date = latest_dividend["paymentDate"]
    latest_ex_dividend_date_as_date = dt.strptime(latest_ex_dividend_date, '%Y-%m-%d')
    one_year_with_wiggle_room_for_weekends = timedelta(days=360)
    one_year_ago = latest_ex_dividend_date_as_date - one_year_with_wiggle_room_for_weekends

    annual_dividend_payment_count = 0
    annual_dividend_amount = 0
    dividend_payment_months = []

    for item in historical_dividends["historical"]:
        item_date = dt.strptime(item["date"], '%Y-%m-%d')
        item_payment_month_number = item_date.month
        item_payment_month = calendar.month_abbr[item_payment_month_number]
        if item_date > one_year_ago:
            annual_dividend_payment_count +=1
            annual_dividend_amount += float(round(item["dividend"], 2))
            dividend_payment_months.append(item_payment_month)

    return {
        "ttm_total_dividend_amount": annual_dividend_amount, 
        "ttm_dividend_payment_count": annual_dividend_payment_count,
        "dividend_payment_months": dividend_payment_months
    }


def combine_dividends_into_annual_dividends(historical_dividends):
    annual_dividends = []
    for payment in historical_dividends:
        payment_year = int(payment["paymentDate"][:4])
        dividend_amount = float(payment["dividend"])
        if any(dictionary.get("year") == payment_year for dictionary in annual_dividends):
            for i in annual_dividends:
                if i["year"] == payment_year:
                    i["total_annual_dividend"] += dividend_amount
        if not any(dictionary.get("year") == payment_year for dictionary in annual_dividends):
            annual_dividends.append({"year": payment_year, "total_annual_dividend": dividend_amount })
    return annual_dividends

def get_consistent_years_dividend_growth(annual_dividends):
    count = 0
    print('list in COUNTER')
    print(annual_dividends)
    div_being_checked = annual_dividends[1]["total_annual_dividend"]
    # remove 2 most recent year because not all divs may be included in first year and second year amount is already assinged as div_being_checked
    full_annual_dividends = annual_dividends[2:]
    
    for dividend in full_annual_dividends:
        if div_being_checked > dividend["total_annual_dividend"]:
            count += 1
            div_being_checked = dividend["total_annual_dividend"]
        else:
            break
    
    return int(count)



def get_years_of_dividend_growth(historical_dividends):
    dividend_growth = {
        # "symbol": "symbol",
        # "max_years_on_record":0,
        # "yoy_growth": 0,
        # "growth_all_years_on_record": None,
        # "annual_dividends": [] # now added after finished completion in combine_dividends_into_annual_dividends
    }
    
    annual_dividends_dict_list = combine_dividends_into_annual_dividends(historical_dividends["historical"])
    dividend_growth["annual_dividends"] = annual_dividends_dict_list
    dividend_growth["max_years_on_record"] = int(len(dividend_growth["annual_dividends"]))
    dividend_growth["symbol"] = historical_dividends["symbol"]
    consistent_growth_years_count = get_consistent_years_dividend_growth(annual_dividends_dict_list)
    dividend_growth["yoy_growth"] = consistent_growth_years_count
    dividend_growth["growth_all_years_on_record"] = True if len(dividend_growth["annual_dividends"]) == dividend_growth["yoy_growth"] else False
    
    # print(dividend_growth)
    return dividend_growth

def get_all_us_tickers():
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    finnhub_stock_listing = finnhub_client.stock_symbols('US')
    us_stocks = {
        "common_stock": [],
        "etp": [],
        "reit": []
    }
    for stock in finnhub_stock_listing:
      if stock["type"] == "Common Stock":
          us_stocks["common_stock"].append({"symbol": stock["symbol"], "description": stock["description"]})
      if stock["type"] == "ETP": 
          us_stocks["etp"].append({"symbol": stock["symbol"], "description": stock["description"]})
      if stock["type"] == "REIT": 
          us_stocks["reit"].append({"symbol": stock["symbol"], "description": stock["description"]})

    return us_stocks
    
  # get common stock, reit, etp(exchange traded product which cna be etf), open end fund(which can be mutual fund)
#   for item in finnhub_stock_listing:
#     if item["type"] not in types:
#         types.append(item["type"])
#     if item["symbol"] == "SCHD":
#         print(item)
#     if item["currency"] not in currencies:
#         currencies.append(item["currency"])
#   print(types)
#   print(currencies)
  # print(finnhub_client.stock_symbols('US'))
  # with open(finnhub_stock_listing) as data_file:
  #   data = json.load(data_file)
#   for item in finnhub_stock_listing:
    # print(v.keys())
    #   print(v['x'], v['y'], v['yr'])
    # # print(row[0])
    # print(v)

    # print(item['symbol'])
    # print(item['description'])

    # activeTickers.append(
    #   {
    #     "ticker": item['symbol'], 
    #     "title": item['description']
    #   }
    # )

def get_company_profile(symbol):
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    finnhub_company_profile = finnhub_client.company_profile2(symbol=symbol)
    company_profile = {
        "industry": finnhub_company_profile["finnhubIndustry"],
        "website": finnhub_company_profile["weburl"],
        "logo": finnhub_company_profile["logo"]
    }
    return company_profile


STOCK = "msft"

company_profile = get_company_profile(STOCK)
# all_us_tickers = get_all_us_tickers()
# get_quarterly_financials(STOCK)
# annual_financials = get_annual_financials(STOCK)
# net_income_loss = get_net_income_loss_from_annual_financials(annual_financials)
# shares_outstanding = get_shares_outstanding_from_annual_financials(annual_financials)
# total_annual_dividend_paid = get_annual_common_stock_total_dividend_paid(annual_financials)
# annualize_dividend_per_share = get_annualized_dividend_per_share(shares_outstanding, total_annual_dividend_paid)
# historical_dividends = get_historical_dividends(STOCK)
# ttm_dividend_per_share_metrics = get_ttm_dividend_per_share_count_and_months(shares_outstanding, historical_dividends)
# years_of_dividend_growth = get_years_of_dividend_growth(historical_dividends)



# EPS = net_income_loss / shares_outstanding
# print("EPS")
# print(EPS)
# print('div per share')
# print(total_annual_dividend_paid)
# print(annualize_dividend_per_share)







con = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

#cursor
cur = con.cursor()


def get_current_stock_price(symbol):
  finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
  quote_response = finnhub_client.quote(symbol)
  current_price = quote_response["c"]
  percent_change = quote_response["dp"]
  previous_close = quote_response["pc"]
  print([quote_response])
  # print(quote_response, current_price, percent_change, previous_close)
  # print('current price: ', current_price, 'percent change: ', percent_change, 'previous close: ', previous_close)
  cur.execute("insert into persons (personid, fullname, jsontest) values (%s, %s, %s)", (10, 'Big Bill', Json(quote_response)))


get_current_stock_price("msft")

# cur.execute("insert into persons (personid, fullname) values (%s, %s)", (2, 'Johny'))

# cur.execute("select * from persons")
# rows = cur.fetchall()

# for r in rows:
#   print(f"id: {r[0]}, name {r[1]}, json {r[2]}")

# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
con.commit()
# close the cursor
cur.close()

if __name__ == "__main__": app.run()

