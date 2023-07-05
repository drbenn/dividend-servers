import psycopg2
import finnhub
from psycopg2.extras import Json
from datetime import datetime as dt
from datetime import time, timedelta, date
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
   "payout_ratio": 15,
   "annual_dividends": 16,
   "years_dividend_growth": 17,
   "dividend_payment_months_and_count": 18,
   "growth_all_years_of_history": 19,
   "three_year_cagr": 20,
   "five_year_cagr": 21
}

connection = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

#cursor
cur = connection.cursor()


def get_company_profiles_and_update_db(dividend_stocks):
    print(dividend_stocks)
    for ticker in dividend_stocks:
      print("ticker in get profile")
      print(ticker)
      finnhub_company_profile = finnhub_client.company_profile2(symbol=ticker)
      industry = finnhub_company_profile["finnhubIndustry"]
      website = finnhub_company_profile["weburl"]
      logo = finnhub_company_profile["logo"]
      query = "UPDATE stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
      cur.execute(query, (industry, website, logo, ticker))
    return True


def get_company_profile(ticker):
  finnhub_company_profile = finnhub_client.company_profile2(symbol=ticker)
  print(finnhub_company_profile)
  company_profile = None
  if finnhub_company_profile:
    industry = finnhub_company_profile["finnhubIndustry"]
    website = finnhub_company_profile["weburl"]
    logo = finnhub_company_profile["logo"]
    company_profile = {
        "industry": industry,
        "website": website,
        "logo": logo
    }
  else:
        company_profile = {
        "industry": "N/A",
        "website": "N/A",
        "logo": "N/A"
    }
  return company_profile


def update_db_with_company_profile(ticker, profile):
  print("profile: ", profile)
  query = "Update stocks set industry = %s, website = %s, logo = %s where ticker = %s"
  cur.execute(query, (profile["industry"], profile["website"], profile["logo"], ticker))
  connection.commit()




def get_quarterly_financials(ticker):
    quarterly_financials = finnhub_client.financials_reported(symbol=ticker, freq='quarterly')
    print("QUARTERLY")
    print(quarterly_financials)
    print("QUARTERLY DUMPS")
    print(json.dumps(quarterly_financials))
    return quarterly_financials

def update_db_with_quarterly_financials(ticker, quarterly_financials):
  print("quarterly financials: ", quarterly_financials)
  json_financials = json.dumps(quarterly_financials)
  query = "Update stocks set quarterly_financials = %s where ticker = %s"
  cur.execute(query, (json_financials, ticker))
  connection.commit()

  

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

def insert_new_tickers_to_db(tickers_to_add_to_db, all_current_us_tickers):
  print("in insert tickers")
  for ticker in tickers_to_add_to_db:
     for ticker_info in all_current_us_tickers:
        if ticker == ticker_info["symbol"]: 
          cur.execute("insert into stocks (ticker, name, equity_type, last_updated) values (%s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"]))



# ------------------------------------------------------------------------------------------------
# ------------------------------  Annual Financials ----------------------------------------------
# ------------------------------------------------------------------------------------------------

def get_annual_financials_and_determine_if_dividends(db_stocks):
  finnhub_api_fetches = 0
  stocks_with_dividends_to_get_more_detail = []
  for item in db_stocks[:2]:
    print(item)
    ticker = item[db_schema['ticker']]
    if item[db_schema["historic_annual_financials"]] == None:
      print(f"Need to get annual financial api fetch for {ticker}")
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
  print("ticker: ", ticker)
  print("is divpayer: ", is_dividend_payer)
  json_financials = json.dumps(annual_financials)
  query = "Update stocks set historic_annual_financials = %s, has_dividend = %s where ticker = %s"
  cur.execute(query, [json_financials, is_dividend_payer, ticker])
  connection.commit()


# ------------------------------------------------------------------------------------------------
# ------------------------------  DIVIDEND HISTORY -----------------------------------------------
# ------------------------------------------------------------------------------------------------


def grab_list_of_dividend_stocks_from_db(connection) -> list[str]:
  cursor = connection.cursor()
  query = """
    SELECT * FROM stocks WHERE has_dividend = True
    """
  cursor.execute(query)
  retrieved_db_data = cursor.fetchall()
  cursor.close()
  list_of_div_stocks = []
  for stock in retrieved_db_data:
    list_of_div_stocks.append(stock[db_schema["ticker"]])
  return list_of_div_stocks


def get_historic_dividends(connection, db_stocks) -> any:
  print("in get historic dividends")
  for ticker in db_stocks[:1]:
    print(f"tikcer in get historic dividend: {ticker}")
    cursor = connection.cursor()
    query = "select * from stocks where ticker = %s"
    cursor.execute(query, (ticker,))
    retrieved_db_data = cursor.fetchall()
    print("retrieved data")
    print(retrieved_db_data)
    print(retrieved_db_data[0][db_schema["historic_dividends"]])
    print(retrieved_db_data[0][db_schema["dividend_yield"]])
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
    print("before current div yield")
    current_dividend_yield = calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_count)
    three_year_cagr = calculate_x_year_cagr(annual_dividends, 3)
    five_year_cagr = calculate_x_year_cagr(annual_dividends, 5)
    # update db
    json_historic_dividends = json.dumps(historic_dividends)
    json_annual_dividends = json.dumps(annual_dividends)
    json_div_pay_months_and_count = json.dumps(dividend_payment_months_and_count)
    query = "Update stocks set historic_dividends = %s, annual_dividends = %s, years_dividend_growth = %s, dividend_payment_months_and_count = %s, growth_all_years_of_history = %s, dividend_yield = %s,three_year_cagr = %s, five_year_cagr = %s where ticker = %s"
    cur.execute(query, [json_historic_dividends, json_annual_dividends, years_dividend_growth, json_div_pay_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker])
    connection.commit()

def combine_dividends_into_annual_dividends(historic_dividends) -> list[object]:
  historic_dividends = historic_dividends["historical"]
  annual_dividends = []
  for payment in historic_dividends:
      print(payment)
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
# ------------------------------  END DIVIDEND HISTORY -----------------------------------------------
# ------------------------------------------------------------------------------------------------

def calculate_dividend_payout_ratio(net_income, dividends_paid):
    dividend_payout_ratio = (dividends_paid / net_income)
    # print(dividend_payout_ratio)







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

# stock details requiring further calculations and use of lower request limit FMP API
db_stocks_with_dividends = grab_list_of_dividend_stocks_from_db(connection)
print("8")
print(db_stocks_with_dividends)
historic_dividends_returned = get_historic_dividends(connection, db_stocks_with_dividends)
print("9")
get_company_profiles_and_update_db(db_stocks_with_dividends)
print("10")


# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
connection.commit()
# close the cursor
cur.close()





