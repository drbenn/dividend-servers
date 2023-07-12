import datetime
import time
import calendar
import schedule
import json
from schedule import repeat, every
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import psycopg2
import finnhub
from api_keys import FINNHUB_API_KEY, FMP_API_KEY


db_schema = {
   "ticker": 0,
   "last_updated": 1,
   "name": 2,
   "equity_type": 3,
   "has_dividend": 4,
   "industry": 5,
   "website": 6,
   "logo": 7,
   "dividend_yield": 8,
   "years_dividend_growth": 9,
   "growth_all_years_of_history": 10,
   "payout_ratios": 11,
   "three_year_cagr": 12,
   "five_year_cagr": 13,
   "year_price_high": 14,
   "year_price_low": 15,
   "beta": 16,
   "backup_stock_price": 17,
   "backup_stock_price_date_saved": 18,
   "dividend_payment_months_and_count": 19,
   "annual_dividends": 20,
   "historic_dividends": 21,
   "basic_financial_metrics": 22,
   "quarterly_financials": 23,
   "historic_annual_financials": 24,
   "basic_financials": 25
}

connection = psycopg2.connect(
  host="localhost",
  database="NewDB",
  user="postgres",
  password="postgres",
  port="5432"
  )

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


# ------------------------------------------------------------------------------
# --------------------  PROPERTIES AND DB EVENT LOG  ---------------------------
# ------------------------------------------------------------------------------

NEVER_UPDATED_CYCLE_ROW_LIMIT = 18000
FMP_API_DAILY_CALL_LIMIT = 10

def add_event_to_run_log(message):
  cur = connection.cursor()
  cur.execute("INSERT INTO grizzly_run_log (time_stamp, summary) values (%s, %s)", (datetime.datetime.now(), message))
  connection.commit()
  cur.close()




# ------------------------------------------------------------------------------
# -------------------  1 of 4 - Update Stock Listing   -------------------------
# ------------------------------------------------------------------------------

def get_all_us_tickers() -> any:
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

def grab_all_db_data(connection) -> any:
  cur = connection.cursor()
  query = "SELECT * FROM grizzly_stocks"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  return retrieved_db_data

def find_tickers_to_add(all_current_us_tickers, all_db_data_no_updates) -> list[str]:
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
        cur = connection.cursor()
        cur.execute("INSERT INTO grizzly_stocks (ticker, name, equity_type) values (%s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"]))
        connection.commit()
        cur.close()


# ------------------------------------------------------------------------------
# -------------------  2 of 4 - Update_stock_has_dividend   --------------------
# ------------------------------------------------------------------------------


def get_never_updated_annual_financials_and_determine_if_dividends(db_stocks) -> any:
  tickers_eligible_for_update = 0
  eligible_ticker_dicts = []

  for item in db_stocks:
    if item[db_schema["has_dividend"]] == None and tickers_eligible_for_update <= NEVER_UPDATED_CYCLE_ROW_LIMIT:
      eligible_ticker_dicts.append(item)
      tickers_eligible_for_update += 1 

  for index, item in enumerate(eligible_ticker_dicts):
    ticker = item[db_schema['ticker']]
    annual_financials = get_annual_financials(ticker)
    is_dividend_payer = determine_if_dividend_payer_from_annual_financials(annual_financials)
    print(f"{index + 1} of {NEVER_UPDATED_CYCLE_ROW_LIMIT} - {ticker} is a dividend payer?: {is_dividend_payer}")
    update_db_with_annual_financials(ticker, is_dividend_payer, annual_financials)
    return


def get_annual_financials(ticker) -> list[object]:
  print(f"calling finnhub for annual financials and testing for dividend of {ticker} @ {datetime.datetime.now()}")
  try:
    annual_financials = finnhub_client.financials_reported(symbol=ticker, freq='annual')
    time.sleep(3) # sleep in seconds - so up to 20 api calls/min
    return annual_financials
  except Exception:
    print("Finnhub api call failed, marking stock as no_dividend")
    update_db_dividend_payer_false( False, ticker)
    return


def determine_if_dividend_payer_from_annual_financials(annual_financials) -> bool:
  if annual_financials == None or annual_financials["data"] == None or len(annual_financials["data"]) == 0:
    return False
  elif len(annual_financials["data"]) > 0:
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
      if item == "PaymentsOfDividendsCommonStock" or item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock":
        return True
  else:
    return False
 
   
def update_db_with_annual_financials(ticker, is_dividend_payer, annual_financials) -> any:
  if is_dividend_payer == True:
    update_db_dividend_payer_true(annual_financials, is_dividend_payer, ticker)
  elif is_dividend_payer == False:
    update_db_dividend_payer_false(is_dividend_payer, ticker)


def update_db_dividend_payer_true(annual_financials, is_dividend_payer, ticker):
  json_financials = json.dumps(annual_financials)
  query = "UPDATE grizzly_stocks SET historic_annual_financials = %s, has_dividend = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_financials, is_dividend_payer, ticker])
  connection.commit()
  cur.close()

def update_db_dividend_payer_false(is_dividend_payer, ticker):
  # if not_dividend_payer last_updated timestamp set for future use in periodic review AND financial NOT stored in database
  query = "UPDATE grizzly_stocks SET has_dividend = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [is_dividend_payer, datetime.datetime.now(), ticker])
  connection.commit()
  cur.close()


# ------------------------------------------------------------------------------
# -------  SINGLE STOCK DIVIDEND HISTORY FMP CALL AND CALCULATIONS   -----------
# ------------------------------------------------------------------------------





def get_historic_dividends(ticker) -> any:
  print(f"ticker in get historic being procesed: {ticker}")
  url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
  try:
    with urlopen(url, timeout=10) as response:
      data = response.read().decode("utf-8")
      historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
      print("historic dividends received")
      print(historic_dividends)
      update_db_with_historic_dividends_and_related_calculations(historic_dividends, ticker)
      print(f"Historic FMP call successful for ticker {ticker}")
      return True
  except HTTPError as error:
    print(f"FMP API CALL HTTPError for ticker {ticker}: {error.status}, {error.reason}")
    return False
  except URLError as error:
    print(f"FMP API CALL URLError for ticker {ticker}: {error.reason}")
    return False
  except TimeoutError:
    print(f"FMP API CALL TimeoutError: Request timed out for ticker {ticker}")
    return False


def update_db_with_historic_dividends_and_related_calculations(historic_dividends, ticker) -> any:
  dividend_history = historic_dividends["historical"]
  if len(dividend_history) == 0:
    # if not_dividend_payer last_updated timestamp set to catch for periodic review AND financial NOT stored in database
    update_db_dividend_payer_false(False, ticker)
  else:
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
    query = "UPDATE grizzly_stocks SET historic_dividends = %s, annual_dividends = %s, years_dividend_growth = %s, dividend_payment_months_and_count = %s, growth_all_years_of_history = %s, dividend_yield = %s,three_year_cagr = %s, five_year_cagr = %s WHERE ticker = %s"
    cur = connection.cursor()
    cur.execute(query, [json_historic_dividends, json_annual_dividends, years_dividend_growth, json_div_pay_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker])
    connection.commit()
    cur.close()

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

  # add yoy linear dividend growth rate
  limit_of_annual_dividends = (len(annual_dividends) - 2)
  for index, annual in enumerate(annual_dividends):
    if index <= limit_of_annual_dividends:
      new_dividend = annual_dividends[index]["total_annual_dividend"]
      old_dividend = annual_dividends[index + 1]["total_annual_dividend"]
      linear_growth_rate = round(float((new_dividend - old_dividend) / old_dividend ), 4 )
      annual_dividends[index]["yoy_linear_growth_rate"] = linear_growth_rate 
  return annual_dividends






























def get_payment_months_and_count(historic_dividends):
  latest_dividend = historic_dividends["historical"][0]
  latest_ex_dividend_date = latest_dividend["date"]
  latest_ex_dividend_date_as_date = datetime.datetime.strptime(latest_ex_dividend_date, '%Y-%m-%d')
  one_year_with_wiggle_room_for_weekends = datetime.timedelta(days=360)
  one_year_ago = latest_ex_dividend_date_as_date - one_year_with_wiggle_room_for_weekends
  annual_dividend_payment_count = 0
  dividend_payment_months = []

  for item in historic_dividends["historical"]:
    item_date = datetime.datetime.strptime(item["date"], '%Y-%m-%d')
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
  if current_price == 0:
     return 0
  else:
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


def get_company_profiles_and_update_db(ticker) -> any:
  finnhub_company_profile = finnhub_client.company_profile2(symbol=ticker)
  industry = finnhub_company_profile["finnhubIndustry"]
  website = finnhub_company_profile["weburl"]
  logo = finnhub_company_profile["logo"]
  query = "UPDATE grizzly_stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (industry, website, logo, ticker))
  connection.commit()
  cur.close()
  return True


def get_basic_financials_and_update_db(ticker) -> any:
  basic_financials = finnhub_client.company_basic_financials(ticker, 'all')
  json_basic_financials = json.dumps(basic_financials)
  year_high = float(basic_financials["metric"]["52WeekHigh"])
  year_low = float(basic_financials["metric"]["52WeekLow"])
  beta = float(basic_financials["metric"]["beta"])
  query = "UPDATE grizzly_stocks SET basic_financials = %s, year_price_high = %s, year_price_low = %s, beta = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (json_basic_financials, year_high, year_low, beta, ticker))
  connection.commit()
  cur.close()
  return True


# ------------------------------------------------------------------------------------------------
# ---------------------------  ANNUAL FINANCIAL STATEMENT CALCS  ---------------------------------
# ------------------------------------------------------------------------------------------------


def calculate_payout_ratios_and_update_db(ticker)  -> str:
  query = "SELECT annual_dividends, historic_annual_financials FROM grizzly_stocks WHERE ticker = %s"
  cur = connection.cursor()
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
        if item["concept"] == "us-gaap_NetIncomeLoss" or item["concept"] == "us-gaap_ProfitLoss":
          netIncomeLoss = float(item["value"])
          payout_ratio = annual_dividend_paid / netIncomeLoss
          annual_payout_ratios.append({ "year": annual["year"], "payout_ratio": payout_ratio, "net_income_loss": item["value"]})

  # update db with payout ratio dict
  json_payouts = json.dumps(annual_payout_ratios)
  cur = connection.cursor()
  query = "UPDATE grizzly_stocks SET payout_ratios = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_payouts, datetime.datetime.now(), ticker])
  connection.commit()
  cur.close()
  return ticker




def grab_db_data_tickers_never_updated_with_has_dividends(connection) -> any:
  cur = connection.cursor()
  query = "SELECT ticker, last_updated FROM grizzly_stocks WHERE has_dividend = True"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  tickers_to_update = []
  for item in retrieved_db_data:
    if item[1] == None:
      tickers_to_update.append(item[0])
  print(tickers_to_update)
  return tickers_to_update

def grab_db_data_tickers_previously_updated_with_has_dividends(connection) -> any:
  cur = connection.cursor()
  # query = "SELECT * FROM stocks WHERE has_dividend = True OR has_dividend = False ORDER BY last_updated ASC"
  query = "SELECT ticker,last_updated FROM grizzly_stocks WHERE has_dividend = True ORDER BY last_updated ASC"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  tickers_to_update = []
  print(retrieved_db_data)
  for item in retrieved_db_data:
    if item[1] == None:
      tickers_to_update.append(item[0])
  print(tickers_to_update)
  return tickers_to_update

def get_consistent_years_dividend_growth(annual_dividends) -> int:
  print("In consistent years")
  print(annual_dividends)
  print(len(annual_dividends))
  list_len = len(annual_dividends)
  print(list_len == 0)
  if list_len == 0:
    return 0
  else:
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


# ------------------------------------------------------------------------------
# ------------------------------   TASKS SCHEDULED   ---------------------------
# ------------------------------------------------------------------------------

@repeat(every().day.at('11:07:00'))
def update_full_us_stock_listing():
  print(f"Running daily task 1 of 4 'update_full_us_stock_listing' @ {datetime.datetime.now()}")
  all_current_us_tickers = get_all_us_tickers()
  all_db_data = grab_all_db_data(connection)
  tickers_to_add_to_db = find_tickers_to_add(all_current_us_tickers, all_db_data)
  insert_new_tickers_to_db(tickers_to_add_to_db, all_current_us_tickers)
  add_event_to_run_log( "Daily stock listing verified and updated")
  print(f"Completed daily task 1 of 4 'update_full_us_stock_listing' @ {datetime.datetime.now()}")


# @repeat(every().day.at('20:33:40'))
def determine_if_never_updated_ticker_has_dividends_on_annual_financials():
  print(f"Running daily task 2 of 4 'determine_if_ticker_has_dividends_financials' @ {datetime.datetime.now()}")
  all_db_data = grab_all_db_data(connection)
  get_never_updated_annual_financials_and_determine_if_dividends(all_db_data)
  add_event_to_run_log( "Daily stock_has_dividened updated")
  print(f"Completed daily task 2 of 4 'determine_if_ticker_has_dividends_financials' @ {datetime.datetime.now()}")


determine_if_never_updated_ticker_has_dividends_on_annual_financials()

@repeat(every().day.at('13:41:25'))
def update_individual_dividend_stock_data():
  print(f"Doing grab has_div no data task at: {datetime.datetime.now()}")
  new_tickers_to_update = grab_db_data_tickers_never_updated_with_has_dividends(connection) 
  for ticker in new_tickers_to_update:
  
    print(f"getting single stock detail of {ticker} @ {datetime.datetime.now()}")
    # 1 FMP API call per stock
    historic_dividends_returned = get_historic_dividends(ticker)
    # ------------ BASIC FINANCIAL CALL UPDATES --------------------
    # get basic financials and update to db 52 week high/low and beta
    get_company_profiles_and_update_db(ticker)
    get_basic_financials_and_update_db(ticker)
    # -------------- ANNUAL FINANCIAL STATEMENT CALCS ----------------
    # no api calls required
    calculate_payout_ratios_and_update_db(ticker)


    time.sleep(3)
    print(f"FINISHED single stock detail of {ticker} @ {datetime.datetime.now()}")
    return



    # api_call_counts = single_ticker_api_and_update_process(ticker)


  previous_tickers_to_update = grab_db_data_tickers_previously_updated_with_has_dividends(connection) 
  # list = [1,2,3,4,5,6,7]
  # for item in list:
  #     print(f"Item {item} at: {datetime.datetime.now()}")
  #     time.sleep(5) # sleep in seconds



# schedule.every(5).seconds.do(task)
# schedule.every().day.at('10:23').do(task) # 15:15 for 3:15 pm


while True:
  schedule.run_pending()
  time.sleep(1)