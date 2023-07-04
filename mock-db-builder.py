import psycopg2
import finnhub
from psycopg2.extras import Json
from datetime import datetime as dt
from datetime import time, timedelta, date
from api_keys import FINNHUB_API_KEY, FMP_API_KEY
import json
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
from urllib.request import urlopen


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
}

connection = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

#cursor
cur = connection.cursor()


# def log_db_insert(insert_summary):
#   now = dt.now()
#   cur.execute("insert into run_log (timestamp, summary) values (%s, %s)", (now, insert_summary))

# def insert_in_db():
#   json_test = [{"name": "Billy", "age": 22}, {"name":"Saul", "age": 55}]
#   cur.execute("insert into persons (personid, fullname, jsontest) values (%s, %s, %s)", (10, 'Big Bill', Json(json_test)))

# insert_in_db()
# log_db_insert("test 2")

# def insert_stock_in_db():
#   now = dt.now()
#   cur.execute("insert into stocks (ticker, name) values (%s, %s)", ("APPL", "APPLE SUCKS"))

# insert_stock_in_db()



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
     #   """Gets all data from the PostgreSQL table."""
    cursor = connection.cursor()
    query = """
      SELECT * FROM stocks
      """
    cursor.execute(query)
    retrieved_db_data = cursor.fetchall()
    cursor.close()
    return retrieved_db_data
   
# def get_company_profiles(updated_db_tickers_full_stock_table):
#     stocks_already_in_db = []
#     for line in updated_db_tickers_full_stock_table:
#         # print(line[2])
#         if line[2] == "common_stock":
#           stocks_already_in_db.append(line[0])
#     small_list = stocks_already_in_db[0:5]
#     print(small_list)
#     for stock in small_list:
#       print(stock)
#       finnhub_company_profile = finnhub_client.company_profile2(symbol=stock)
#       industry = finnhub_company_profile["finnhubIndustry"]
#       website = finnhub_company_profile["weburl"]
#       logo = finnhub_company_profile["logo"]
#       company_profile = {
#           "industry": industry,
#           "website": website,
#           "logo": logo
#       }
#       now = dt.now()
#       cur.execute("""UPDATE stocks SET industry = %s website = %s logo = %s WHERE ticker = %s"""), (industry, website, logo, stock)
#     # return company_profile

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
          now = dt.now()     
          cur.execute("insert into stocks (ticker, name, equity_type, last_updated) values (%s, %s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"], now))



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
  query = "Update stocks set industry = %s, website = %s, logo = %s, last_updated = %s where ticker = %s"
  cur.execute(query, (profile["industry"], profile["website"], profile["logo"], dt.now(), ticker))
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
  query = "Update stocks set quarterly_financials = %s, last_updated = %s where ticker = %s"
  cur.execute(query, (json_financials, dt.now(), ticker))
  connection.commit()


# def find_empty_columns_for_associated_api_fetches_and_dispatch_api_fetches(db_stocks):
#   finnhub_api_fetches = 0
#   for item in db_stocks[:2]:
#     print(item)
#     ticker = item[db_schema['ticker']]

#     # if item[db_schema["historic_dividends"]] == None:
#     #   print(f"Need to get historic dividends api fetch for {ticker}")


#     # if item[db_schema["industry"]] == None:
#     #   print(f"Need to get company profile api fetch for {ticker}")
#     #   profile = get_company_profile(ticker)
#     #   update_db_with_company_profile(ticker, profile)
#     #   finnhub_api_fetches += 1

#     # if item[db_schema["historic_annual_financials"]] == None:
#     #   print(f"Need to get annual financial api fetch for {ticker}")
#     #   annual_financials = get_annual_financials(ticker)
#     #   update_db_with_annual_financials(ticker, annual_financials)
#     #   finnhub_api_fetches += 1

#     # if item[db_schema["quarterly_financials"]] == None:
#     #   print(f"Need to get quarterly financials api fetch for {ticker}")
#     #   quarterly_financials = get_quarterly_financials(ticker)
#     #   update_db_with_quarterly_financials(ticker, quarterly_financials)
#     #   finnhub_api_fetches += 1



#     # if item[db_schema["basic_financial_metrics"]] == None:
#     #   print(f"Need to get basic financial metrics api fetch for {ticker}")
  
#   print(f"finnnhub total calls: {finnhub_api_fetches}")

            # cur.execute("insert into stocks (ticker, name, equity_type, last_updated) values (%s, %s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"], now))
  
# def update_db_with_historic_dividends_and_has_dividend_bool(ticker, historic_dividends):
#   print("ticker: ", ticker)
#   print("historic_dividends_dict: ", historic_dividends)
#   print(historic_dividends["historical"])
#   print(f"length: {historic_dividends['historical']}")
#   print(f"first: {historic_dividends['historical'][0]}")
#   print(f"first LEN: {len(historic_dividends['historical'][0])}")
#   dividend_history_list = historic_dividends["historical"]
#   json_dividend_history = json.dumps(dividend_history_list)
#   if len(dividend_history_list) < 1:
#     query = "Update stocks set has_dividend = %s, historic_dividends = %s, last_updated = %s where ticker = %s"
#     cur.execute(query, (False, json_dividend_history, dt.now(), ticker))
#     connection.commit()
#   if len(dividend_history_list) > 0:
#     query = "Update stocks set has_dividend = %s, historic_dividends = %s, last_updated = %s where ticker = %s"
#     cur.execute(query, (True, json_dividend_history, dt.now(), ticker))
#     connection.commit()
#   return
     
  # query = "Update stocks set industry = %s, website = %s, logo = %s, last_updated = %s where ticker = %s"
  # cur.execute(query, (profile["industry"], profile["website"], profile["logo"], dt.now(), ticker))
  # connection.commit()

# def get_historic_dividends_and_set_has_dividend_boolean(db_stocks):
#   for item in db_stocks[:1]:
#     print(item)
#     ticker = item[db_schema['ticker']]
#     if item[db_schema["historic_dividends"]] == None:
#       print(f"Need to get historic dividends api fetch for {ticker}")
#       url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
#       response = urlopen(url)
#       data = response.read().decode("utf-8")
#       # print(json.loads(data))
#       historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
#       update_db_with_historic_dividends_and_has_dividend_bool(ticker, historic_dividends)
#       return

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
  query = "Update stocks set historic_annual_financials = %s, has_dividend = %s, last_updated = %s where ticker = %s"
  cur.execute(query, [json_financials, is_dividend_payer, dt.now(), ticker])
  connection.commit()



# ------------------------------------------------------------------------------------------------
# ------------------------------  End Annual Financials ------------------------------------------
# ------------------------------------------------------------------------------------------------



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
  for ticker in db_stocks[:1]:
    print(ticker)
    cursor = connection.cursor()
    query = "select * from stocks where ticker = %s"
    cursor.execute(query, (ticker,))
    retrieved_db_data = cursor.fetchall()
    cursor.close()
    print(retrieved_db_data[0][db_schema["historic_dividends"]])
    if retrieved_db_data[0][db_schema["historic_dividends"]] == None: # TODO: add condition based on last update/or last div/etc for updating after initial historic div load
      
      # get historic dividends from FMP
      url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
      response = urlopen(url)
      data = response.read().decode("utf-8")
      historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
      print(historic_dividends)
      # TODO calculations on historic dividends
      annual_dividends = combine_dividends_into_annual_dividends(historic_dividends)
      years_dividend_growth = get_consistent_years_dividend_growth(annual_dividends)
      print("YEARS GROWTH")
      print(years_dividend_growth)
      # growth_all_years_of_history = somefunction()
      # TODO update historic dividends and related calculation in db



def combine_dividends_into_annual_dividends(historic_dividends) -> list[object]:
  historic_dividends = historic_dividends["historical"]
  annual_dividends = []
  for payment in historic_dividends:
      # listed year of most recent payment date
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

# ------------------------------------------------------------------------------------------------
# ------------------------------  DIVIDEND HISTORY -----------------------------------------------
# ------------------------------------------------------------------------------------------------


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
get_historic_dividends(connection, db_stocks_with_dividends)
# get_company_profiles(updated_db_tickers_full_stock_table)
# updated_db_tickers_dividend_stocks_only = grab_all_db_data(connection)
# get_historic_dividends_and_set_has_dividend_boolean(updated_db_tickers_full_stock_table)
# data_endpoints_needed_for_ticker_updates = find_empty_columns_for_associated_api_fetches_and_dispatch_api_fetches(updated_db_tickers_full_stock_table)


# def getsome():
#   finnhub_company_profile = finnhub_client.company_profile2(symbol="XMTF")
#   print(finnhub_company_profile)

# getsome()
   # def get_all_table_data(connection):
#   """Gets all data from the PostgreSQL table."""
#   cursor = connection.cursor()
#   query = """
#     SELECT *
#     FROM timestamp
#   """
#   cursor.execute(query)
#   data = cursor.fetchall()
#   cursor.close()
#   return data















# cur.execute("insert into persons (personid, fullname) values (%s, %s)", (2, 'Johny'))

# cur.execute("select * from persons")
# rows = cur.fetchall()

# for r in rows:
#   print(f"id: {r[0]}, name {r[1]}, json {r[2]}")

# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
connection.commit()
# close the cursor
cur.close()





