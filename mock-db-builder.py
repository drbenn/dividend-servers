import psycopg2
import finnhub
from psycopg2.extras import Json
from datetime import datetime as dt
from datetime import timedelta
from api_keys import FINNHUB_API_KEY, FMP_API_KEY
import json
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
from urllib.request import urlopen
import calendar


db_schema = {
   "ticker": 0,
   "last_updated": 1,
   "name": 2,
   "equity_type": 3,
   "industry": 4,
   "website": 5,
   "logo": 6,
   "historic_dividends": 7,
   "has_dividend": 8,
   "historic_annual_financials": 9,
   "quarterly_financials": 10,
   "basic_financial_metrics": 11,
   "backup_stock_price": 12,
   "backup_stock_price_date_saved": 13,
   "dividend_yield": 14,
   "payout_ratios": 15,
   "annual_dividends": 16,
   "years_dividend_growth": 17,
   "dividend_payment_months_and_count": 18,
   "growth_all_years_of_history": 19,
   "three_year_cagr": 20,
   "five_year_cagr": 21,
   "basic_financials": 22,
   "year_price_high": 23,
   "year_price_low": 24,
   "beta": 25
}

connection = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

#cursor
cur = connection.cursor()

# def get_quarterly_financials(ticker):
#     quarterly_financials = finnhub_client.financials_reported(symbol=ticker, freq='quarterly')
#     print("QUARTERLY")
#     print(quarterly_financials)
#     print("QUARTERLY DUMPS")
#     print(json.dumps(quarterly_financials))
#     return quarterly_financials


# def update_db_with_quarterly_financials(ticker, quarterly_financials):
#   print("quarterly financials: ", quarterly_financials)
#   json_financials = json.dumps(quarterly_financials)
#   query = "Update stocks set quarterly_financials = %s where ticker = %s"
#   cur.execute(query, (json_financials, ticker))
#   connection.commit()

  

# ------------------------------------------------------------------------------------------------
# ------------------------------  DAILY TASKS -----------------------------------------------
# ------------------------------------------------------------------------------------------------


def get_all_us_tickers():
  finnhub_stock_listing = finnhub_client.stock_symbols('US')
  us_stocks =[]
  for stock in finnhub_stock_listing:
    if stock["type"] == "Common Stock":
        us_stocks.append({"symbol": stock["symbol"], "description": stock["description"], "type": "common_stock" })
    if stock["type"] == "ETP": 
        us_stocks.append({"symbol": stock["symbol"], "description": stock["description"], "type": "etp"})
    if stock["type"] == "REIT": 
        us_stocks.append({"symbol": stock["symbol"], "description": stock["description"], "type": "reit"})
  return us_stocks


def grab_all_db_data(connection):
  cursor = connection.cursor()
  query = "SELECT * FROM stocks"
  cursor.execute(query)
  retrieved_db_data = cursor.fetchall()
  cursor.close()
  return retrieved_db_data


def find_tickers_to_add(all_current_us_tickers, all_db_data_no_updates):
  stocks_already_in_db = []
  for line in all_db_data_no_updates:
      stocks_already_in_db.append(line[db_schema["ticker"]])
  tickers_to_add_to_db = []
  for stock in all_current_us_tickers:
    if stock["symbol"] not in stocks_already_in_db:
       tickers_to_add_to_db.append(stock["symbol"])
  return tickers_to_add_to_db


def insert_new_tickers_to_db(tickers_to_add_to_db, all_current_us_tickers) -> any:
  for ticker in tickers_to_add_to_db:
     for ticker_info in all_current_us_tickers:
        if ticker == ticker_info["symbol"]: 
          cur.execute("INSERT INTO stocks (ticker, name, equity_type) values (%s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"]))
          connection.commit()



# ------------------------------------------------------------------------------------------------
# ------------------------------  Annual Financials ----------------------------------------------
# ------------------------------------------------------------------------------------------------

def get_annual_financials_and_determine_if_dividends(db_stocks):
  finnhub_api_fetches = 0
  stocks_with_dividends_to_get_more_detail = []
  for item in db_stocks[:2]:
    ticker = item[db_schema['ticker']]
    if item[db_schema["historic_annual_financials"]] == None:
      annual_financials = get_annual_financials(ticker)
      is_dividend_payer = determine_if_dividend_payer_from_annual_financials(annual_financials)
      update_db_with_annual_financials(ticker, is_dividend_payer, annual_financials)
      finnhub_api_fetches += 1
      if is_dividend_payer:
        stocks_with_dividends_to_get_more_detail.append(ticker)
  return stocks_with_dividends_to_get_more_detail 


def get_annual_financials(ticker) -> list[object]:
    annual_financials = finnhub_client.financials_reported(symbol=ticker, freq='annual')
    return annual_financials


def determine_if_dividend_payer_from_annual_financials(annual_financials) -> bool:
    if len(annual_financials["data"]) == 0 or annual_financials["data"] == None:
      return False
    elif len(annual_financials["data"]) > 0:
      cashflow_statement = annual_financials["data"][0]["report"]["cf"]
      for item in cashflow_statement:
        if item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock":
            return True
    else:
      return False
 
   
def update_db_with_annual_financials(ticker, is_dividend_payer, annual_financials) -> any:
  json_financials = json.dumps(annual_financials)
  query = "UPDATE stocks SET historic_annual_financials = %s, has_dividend = %s WHERE ticker = %s"
  cur.execute(query, [json_financials, is_dividend_payer, ticker])
  connection.commit()


# ------------------------------------------------------------------------------------------------
# ------------------------------  DIVIDEND HISTORY -----------------------------------------------
# ------------------------------------------------------------------------------------------------

# TODO: Update tickers based on last_updated, which is only updated on last actions, which is now going to be considered payout ratio, so rewrite all code so that instead of looping through db_stocks_with_dividends for each operation, each stock should go through all operations so it can actually complete a full row of data and THEN move on to the next stock to fully update
def grab_list_of_dividend_stocks_from_db(connection) -> list[str]:
  cursor = connection.cursor()
  query = "SELECT * FROM stocks WHERE has_dividend = True"
  cursor.execute(query)
  retrieved_db_data = cursor.fetchall()
  cursor.close()
  list_of_div_stocks = []
  for stock in retrieved_db_data:
    list_of_div_stocks.append(stock[db_schema["ticker"]])
  return list_of_div_stocks


def get_historic_dividends(connection, db_stocks) -> any:
  for ticker in db_stocks[:1]:
    cursor = connection.cursor()
    query = "SELECT * from stocks WHERE ticker = %s"
    cursor.execute(query, (ticker,))
    retrieved_db_data = cursor.fetchall()
    cursor.close()
    if retrieved_db_data[0][db_schema["historic_dividends"]] == None: # TODO: add condition based on last update/or last div/etc for updating after initial historic div load
      url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
      response = urlopen(url)
      data = response.read().decode("utf-8")
      historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
      update_db_with_historic_dividends_and_related_calculations(historic_dividends, ticker)
      return True
    else:
       return False


def update_db_with_historic_dividends_and_related_calculations(historic_dividends, ticker) -> any:
    annual_dividends = combine_dividends_into_annual_dividends(historic_dividends)
    years_dividend_growth = get_consistent_years_dividend_growth(annual_dividends)
    dividend_payment_months_and_count = get_payment_months_and_count(historic_dividends)
    growth_all_years_of_history = len(annual_dividends) == years_dividend_growth
    current_dividend_yield = calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_count)
    three_year_cagr = calculate_x_year_cagr(annual_dividends, 3)
    five_year_cagr = calculate_x_year_cagr(annual_dividends, 5)
    # update db
    json_historic_dividends = json.dumps(historic_dividends)
    json_annual_dividends = json.dumps(annual_dividends)
    json_div_pay_months_and_count = json.dumps(dividend_payment_months_and_count)
    query = "UPDATE stocks SET historic_dividends = %s, annual_dividends = %s, years_dividend_growth = %s, dividend_payment_months_and_count = %s, growth_all_years_of_history = %s, dividend_yield = %s,three_year_cagr = %s, five_year_cagr = %s WHERE ticker = %s"
    cur.execute(query, [json_historic_dividends, json_annual_dividends, years_dividend_growth, json_div_pay_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker])
    connection.commit()


def combine_dividends_into_annual_dividends(historic_dividends) -> list[object]:
  historic_dividends = historic_dividends["historical"]
  annual_dividends = []
  for payment in historic_dividends:
      # listed year of most recent payment date
      if len(payment["paymentDate"][:4]) > 0:
        payment_year = int(payment["paymentDate"][:4])
        dividend_amount = float(payment["dividend"])
        if any(dictionary.get("year") == payment_year for dictionary in annual_dividends):
            for i in annual_dividends:
                if i["year"] == payment_year:
                    i["total_annual_dividend"] += dividend_amount
        if not any(dictionary.get("year") == payment_year for dictionary in annual_dividends):
            annual_dividends.append({"year": payment_year, "total_annual_dividend": dividend_amount })
  return annual_dividends


def get_consistent_years_dividend_growth(annual_dividends) -> int:
    count = 0
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

def get_payment_months_and_count(historic_dividends):
    latest_dividend = historic_dividends["historical"][0]
    latest_ex_dividend_date = latest_dividend["date"]
    latest_ex_dividend_date_as_date = dt.strptime(latest_ex_dividend_date, '%Y-%m-%d')
    one_year_with_wiggle_room_for_weekends = timedelta(days=360)
    one_year_ago = latest_ex_dividend_date_as_date - one_year_with_wiggle_room_for_weekends
    annual_dividend_payment_count = 0
    dividend_payment_months = []

    for item in historic_dividends["historical"]:
        item_date = dt.strptime(item["date"], '%Y-%m-%d')
        item_payment_month_number = item_date.month
        item_payment_month = calendar.month_abbr[item_payment_month_number]
        if item_date > one_year_ago:
            annual_dividend_payment_count +=1
            dividend_payment_months.append(item_payment_month)

    return {
        "ttm_dividend_payment_count": annual_dividend_payment_count,
        "dividend_payment_months": dividend_payment_months
    }


def calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_counts) -> float:
  current_quote = finnhub_client.quote(ticker)
  current_price = current_quote["c"]
  payments_per_year = dividend_payment_months_and_counts["ttm_dividend_payment_count"]
  ttm_dividends = 0
  for item in historic_dividends["historical"][:payments_per_year]:
    ttm_dividends += float(item["dividend"])
  current_dividend_yield = round(float((ttm_dividends / current_price)), 4)
  return current_dividend_yield

def calculate_x_year_cagr(annual_dividends, years) -> float:
  if len(annual_dividends) >= years + 2:
    beginning_balance = float(annual_dividends[years + 1]["total_annual_dividend"])
    ending_balance = float(annual_dividends[1]["total_annual_dividend"]) # most recent year with all dividends
    cagr = round(float(((ending_balance / beginning_balance) ** ( 1 / years ))  - 1), 4)
    return cagr
  else:
      return 0


# ------------------------------------------------------------------------------------------------
# ---------------------------  BASIC FINANCIAL CALL UPDATES   ------------------------------------
# ------------------------------------------------------------------------------------------------


def get_company_profiles_and_update_db(dividend_stocks) -> any:
  print(dividend_stocks)
  for ticker in dividend_stocks:
    finnhub_company_profile = finnhub_client.company_profile2(symbol=ticker)
    industry = finnhub_company_profile["finnhubIndustry"]
    website = finnhub_company_profile["weburl"]
    logo = finnhub_company_profile["logo"]
    query = "UPDATE stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
    cur.execute(query, (industry, website, logo, ticker))
    connection.commit()
  return True


def get_basic_financials_and_update_db(dividend_stocks) -> any:
  for ticker in dividend_stocks:
    basic_financials = finnhub_client.company_basic_financials(ticker, 'all')
    json_basic_financials = json.dumps(basic_financials)
    year_high = float(basic_financials["metric"]["52WeekHigh"])
    year_low = float(basic_financials["metric"]["52WeekLow"])
    beta = float(basic_financials["metric"]["beta"])
    cur = connection.cursor()
    query = "UPDATE stocks SET basic_financials = %s, year_price_high = %s, year_price_low = %s, beta = %s WHERE ticker = %s"
    cur.execute(query, (json_basic_financials, year_high, year_low, beta, ticker))
    connection.commit()
  return True
    

# ------------------------------------------------------------------------------------------------
# ---------------------------  ANNUAL FINANCIAL STATEMENT CALCS  ---------------------------------
# ------------------------------------------------------------------------------------------------


# def calculate_payout_ratios_and_update_db(net_income, dividends_paid):
def calculate_payout_ratios_and_update_db(dividend_stocks)  -> list[object]:
  for ticker in dividend_stocks:
    cur = connection.cursor()
    query = "SELECT annual_dividends, historic_annual_financials FROM stocks WHERE ticker = %s"
    cur.execute(query, (ticker,))
    data = cur.fetchall()
    cur.close()
    annual_dividends = data[0][0]
    annual_financials = data[0][1]["data"]
    annual_payout_ratios = []

    for annual in annual_financials:
       if any(dictionary.get("year") == annual["year"] for dictionary in annual_dividends):
         annual_dividend_dictionary = None
         for dividend_dict in annual_dividends:
            if dividend_dict["year"] == annual["year"]:
               annual_dividend_dictionary = dividend_dict

         annual_dividend_paid = float(annual_dividend_dictionary["total_annual_dividend"])
         cash_flow_statement = annual["report"]["cf"]
         for item in cash_flow_statement:
            if item["concept"] == "us-gaap_NetIncomeLoss":
              netIncomeLoss = float(item["value"])
              payout_ratio = annual_dividend_paid / netIncomeLoss
              annual_payout_ratios.append({ "year": annual["year"], "payout_ratio": payout_ratio, "net_income_loss": item["value"]})

    # update db with payout ratio dict
    json_payouts = json.dumps(annual_payout_ratios)
    cur = connection.cursor()
    query = "UPDATE stocks SET payout_ratios = %s, last_updated = %s WHERE ticker = %s"
    cur.execute(query, [json_payouts, dt.now(), ticker])
    connection.commit()



# ------------------------------------------------------------------------------------------------
# ---------------------------  FUNCTION CALL QUEUE   ---------------------------------------------
# ------------------------------------------------------------------------------------------------

# ANNUAL TASKS SECTION
# Daily task check for new stocks and if it has dividends as prerequisite for doing more data pulls
print("1")
all_current_us_tickers = get_all_us_tickers()
print("2")
all_db_data_no_updates = grab_all_db_data(connection)
print("3")
tickers_to_add_to_db = find_tickers_to_add(all_current_us_tickers, all_db_data_no_updates)
print("4")
insert_new_tickers_to_db(tickers_to_add_to_db, all_current_us_tickers)
print("5")
updated_db_tickers_full_stock_table = grab_all_db_data(connection)
print("6")
stocks_with_dividends_to_get_more_detail =  get_annual_financials_and_determine_if_dividends(updated_db_tickers_full_stock_table)
print("7")

# DIVIDEND HISTORY SECTION
# stock details requiring further calculations and use of lower request limit FMP API
db_stocks_with_dividends = grab_list_of_dividend_stocks_from_db(connection)
print("8")
print(db_stocks_with_dividends)
historic_dividends_returned = get_historic_dividends(connection, db_stocks_with_dividends)
print("9")

# BASIC FINANCIAL CALL UPDATES
# get basic financials and update to db 52 week high/low and beta

get_company_profiles_and_update_db(db_stocks_with_dividends)
print("10")
get_basic_financials_and_update_db(db_stocks_with_dividends)
print("11")

# ANNUAL FINANCIAL STATEMENT CALCS
calculate_payout_ratios_and_update_db(db_stocks_with_dividends)
print("12")

# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
connection.commit()
# close the cursor
cur.close()