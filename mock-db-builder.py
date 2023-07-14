import psycopg2
import finnhub
from psycopg2.extras import Json
from datetime import datetime as dt
from datetime import timedelta
from api_keys import FINNHUB_API_KEY, FMP_API_KEY
import json
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import calendar


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

# CREATE TABLE stocks (
# 	ticker VARCHAR PRIMARY KEY,
# 	last_updated TIMESTAMP WITH TIME ZONE,
# 	name VARCHAR ( 75 ),
# 	equity_type VARCHAR ( 15 ),
#  	has_dividend BOOLEAN,
# 	industry VARCHAR ( 75 ),
# 	website VARCHAR ( 100 ),
# 	logo VARCHAR ( 100 ),
# 	dividend_yield NUMERIC,
# 	years_dividend_growth NUMERIC,
# 	growth_all_years_of_history BOOLEAN,
# 	payout_ratios JSONB,
# 	three_year_cagr NUMERIC,
# 	five_year_cagr NUMERIC,
# 	year_price_high NUMERIC,
# 	year_price_low NUMERIC,
# 	beta NUMERIC,
# 	backup_stock_price NUMERIC,
# 	backup_stock_price_date_saved TIMESTAMP WITH TIME ZONE,
# 	dividend_payment_months_and_count JSONB,
# 	annual_dividends JSONB,
# 	historic_dividends JSONB,
# 	basic_financial_metrics JSONB,
# 	quarterly_financials JSONB,
# 	historic_annual_financials JSONB,
# 	basic_financials JSONB
# );

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
  query = "SELECT * FROM stocks"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  return retrieved_db_data

def grab_all_db_data_ascending_bgy_date(connection) -> any:
  cur = connection.cursor()
  query = "SELECT * FROM stocks WHERE has_dividend = True OR has_dividend = False ORDER BY last_updated ASC"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
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
          cur = connection.cursor()
          cur.execute("INSERT INTO stocks (ticker, name, equity_type) values (%s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"]))
          connection.commit()
          cur.close()



# ------------------------------------------------------------------------------------------------
# ------------------------------  Annual Financials ----------------------------------------------
# ------------------------------------------------------------------------------------------------
CYCLE_ROW_LIMIT = 10

def get_never_updated_annual_financials_and_determine_if_dividends(db_stocks) -> any:

  tickers_eligible_for_update = 0
  eligible_ticker_dicts = []
  finnhub_api_fetches = 0
  stocks_with_dividends_to_get_more_detail = []


  for item in db_stocks:
    if item[db_schema["has_dividend"]] == None and tickers_eligible_for_update <= CYCLE_ROW_LIMIT:
      eligible_ticker_dicts.append(item)
      tickers_eligible_for_update += 1 

  for item in eligible_ticker_dicts:
    ticker = item[db_schema['ticker']]
    print(f"ticker getting financials and testing for dividend: {ticker}")

    annual_financials = get_annual_financials(ticker)
    is_dividend_payer = determine_if_dividend_payer_from_annual_financials(annual_financials)
    print(f"{ticker} is a dividend payer?: {is_dividend_payer}")
    update_db_with_annual_financials(connection, ticker, is_dividend_payer, annual_financials)
    finnhub_api_fetches += 1
    if is_dividend_payer:
      stocks_with_dividends_to_get_more_detail.append(ticker)
  return stocks_with_dividends_to_get_more_detail 


def get_previously_updated_annual_financials_and_for_review(db_stocks) -> any:
  # db_stocks to be received in ascending order by last_updated 
  tickers_eligible_for_update = 0
  eligible_ticker_dicts = []
  finnhub_api_fetches = 0
  stocks_with_dividends_to_get_more_detail = []

  for item in db_stocks:
    if item[db_schema["has_dividend"]] == False or item[db_schema["has_dividend"]] == True and tickers_eligible_for_update <= CYCLE_ROW_LIMIT:
      eligible_ticker_dicts.append(item)
      tickers_eligible_for_update += 1 

  for item in eligible_ticker_dicts:
    ticker = item[db_schema['ticker']]
    print(f"ticker getting financials and testing for dividend: {ticker}")

    annual_financials = get_annual_financials(ticker)
    is_dividend_payer = determine_if_dividend_payer_from_annual_financials(annual_financials)
    print(f"{ticker} is a dividend payer?: {is_dividend_payer}")
    update_db_with_annual_financials(connection, ticker, is_dividend_payer, annual_financials)
    finnhub_api_fetches += 1
    if is_dividend_payer:
      stocks_with_dividends_to_get_more_detail.append(ticker)
  return stocks_with_dividends_to_get_more_detail 


def get_annual_financials(ticker) -> list[object]:
  annual_financials = finnhub_client.financials_reported(symbol=ticker, freq='annual')
  return annual_financials


def determine_if_dividend_payer_from_annual_financials(annual_financials) -> bool:
  has_dividend = False
  if len(annual_financials["data"]) == 0 or annual_financials["data"] == None:
    has_dividend = False
  elif len(annual_financials["data"]) > 0:
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
      if item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock":
          has_dividend = True
  else:
    has_dividend = False
  if has_dividend == None:
    has_dividend = False
  return has_dividend
 
   
def update_db_with_annual_financials(connection, ticker, is_dividend_payer, annual_financials) -> any:
  json_financials = json.dumps(annual_financials)
  if is_dividend_payer == True:
    query = "UPDATE stocks SET historic_annual_financials = %s, has_dividend = %s WHERE ticker = %s"
    cur = connection.cursor()
    cur.execute(query, [json_financials, is_dividend_payer, ticker])
    connection.commit()
    cur.close()
  if is_dividend_payer == False:
    # if not_dividend_payer last_updated timestamp set to catch for periodic review
    query = "UPDATE stocks SET historic_annual_financials = %s, has_dividend = %s, last_updated = %s WHERE ticker = %s"
    cur = connection.cursor()
    cur.execute(query, [json_financials, is_dividend_payer, dt.now(), ticker])
    connection.commit()
    cur.close()


# ------------------------------------------------------------------------------------------------
# ------------------------------  DIVIDEND HISTORY -----------------------------------------------
# ------------------------------------------------------------------------------------------------

# TODO: Update tickers based on last_updated, which is only updated on last actions, which is now going to be considered payout ratio, so rewrite all code so that instead of looping through db_stocks_with_dividends for each operation, each stock should go through all operations so it can actually complete a full row of data and THEN move on to the next stock to fully update
def grab_list_of_never_updated_dividend_stocks_from_db(connection) -> list[str]:
  query = "SELECT * FROM stocks WHERE has_dividend = True and last_updated IS NULL"
  cur = connection.cursor()
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  list_of_div_stocks = []
  for stock in retrieved_db_data:
    print("retrieved stock db row")
    print(stock[db_schema["ticker"]])
    print(stock[db_schema["name"]])
    print(stock[db_schema["last_updated"]])
    list_of_div_stocks.append(stock[db_schema["ticker"]])
  return list_of_div_stocks

def grab_list_of_previously_updated_dividend_stocks_from_db(connection) -> list[str]:
  query = "SELECT * FROM stocks WHERE has_dividend = True and last_updated IS NULL"
  cur = connection.cursor()
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  list_of_div_stocks = []
  for stock in retrieved_db_data:
    print("retrieved stock db row")
    print(stock[db_schema["ticker"]])
    print(stock[db_schema["name"]])
    print(stock[db_schema["last_updated"]])
    list_of_div_stocks.append(stock[db_schema["ticker"]])
  return list_of_div_stocks


def get_historic_dividends(connection, ticker) -> any:
  print(f"ticker in get historic being procesed: {ticker}")
  query = "SELECT * from stocks WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (ticker,))
  retrieved_db_data = cur.fetchall()
  cur.close()
  if retrieved_db_data[0][db_schema["historic_dividends"]] == None: # TODO: add condition based on last update/or last div/etc for updating after initial historic div load
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
    try:
      with urlopen(url, timeout=10) as response:
        data = response.read().decode("utf-8")
        historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
        update_db_with_historic_dividends_and_related_calculations(connection, historic_dividends, ticker)
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
  else:
      return False


def update_db_with_historic_dividends_and_related_calculations(connection, historic_dividends, ticker) -> any:
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
  query = "UPDATE stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
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
  query = "UPDATE stocks SET basic_financials = %s, year_price_high = %s, year_price_low = %s, beta = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (json_basic_financials, year_high, year_low, beta, ticker))
  connection.commit()
  cur.close()
  return True
    

# ------------------------------------------------------------------------------------------------
# ---------------------------  ANNUAL FINANCIAL STATEMENT CALCS  ---------------------------------
# ------------------------------------------------------------------------------------------------


def calculate_payout_ratios_and_update_db(ticker)  -> str:
  query = "SELECT annual_dividends, historic_annual_financials FROM stocks WHERE ticker = %s"
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
  query = "UPDATE stocks SET payout_ratios = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_payouts, dt.now(), ticker])
  connection.commit()
  cur.close()
  return ticker

# ------------------------------------------------------------------------------------------------
# -----------------------  SINGLE TICKER UPDATE API CALL PROCESS   -------------------------------
# ------------------------------------------------------------------------------------------------

def single_ticker_api_and_update_process(ticker) -> any:
  fmp_api_call_count = 0
  finnhub_api_call_count = 0
  print("8")
  # 1 FMP API call per stock
  historic_dividends_returned = get_historic_dividends(connection, ticker)
  fmp_api_call_count += 1
  # ------------ BASIC FINANCIAL CALL UPDATES --------------------
  # get basic financials and update to db 52 week high/low and beta
  print("9")
  get_company_profiles_and_update_db(ticker)
  finnhub_api_call_count += 1
  print("10")
  get_basic_financials_and_update_db(ticker)
  finnhub_api_call_count += 1
  # -------------- ANNUAL FINANCIAL STATEMENT CALCS ----------------
  print("11")
  # no api calls required
  calculate_payout_ratios_and_update_db(ticker)
  # updated_ticker_to_remove_from_queue = calculate_payout_ratios_and_update_db(ticker)
  # print("DONE -API CALLS complete for 1 stock and db updated w/last_updated")
  # print(f"stocks_to_update_queue: {stocks_to_update_queue}")
  # print(f"ticker to remove from queue: {updated_ticker_to_remove_from_queue}")
  # stocks_to_update_queue.remove(updated_ticker_to_remove_from_queue)
  # print(f"updated queue after removal: {stocks_to_update_queue}")
  return {"fmp_api_call_count": fmp_api_call_count, "finnhub_api_call_count": finnhub_api_call_count}

# ------------------------------------------------------------------------------------------------
# ---------------------------  FUNCTION CALL QUEUE   ---------------------------------------------
# ------------------------------------------------------------------------------------------------


# stocks_to_update_queue = []
finnhub_api_call_count = 0
fmp_api_call_count = 0

# ANNUAL TASKS SECTION
# Daily task check for new stocks and if it has dividends as prerequisite for doing more data pulls

print("1")
all_current_us_tickers = get_all_us_tickers()
finnhub_api_call_count += 1

print("2")
# no api calls required
all_db_data_no_updates = grab_all_db_data(connection)

print("3")
# no api calls required
tickers_to_add_to_db = find_tickers_to_add(all_current_us_tickers, all_db_data_no_updates)

print("4")
# no api calls required
insert_new_tickers_to_db(tickers_to_add_to_db, all_current_us_tickers)

print("5")
# no api calls required
updated_db_tickers_full_stock_table = grab_all_db_data(connection)

# intensive per ticker api calls below

print("6")
# will use get_annual_financials as the control flow, upper limit if 10 financial grabs per cycle, if all 10 have dividends that would result in 10 FMP calls(250 daily limit) and 20 more finnhub calls(limit 60/minute and 30/second) - with potential total of 31 total finnhub calls in the cycle(includes 1 call for all stocks daily) 
never_updated_stocks_with_dividends_to_get_more_detail =  get_never_updated_annual_financials_and_determine_if_dividends(updated_db_tickers_full_stock_table)
# finnhub_api_call_count += x - 1 call can be false for dividend, or it can be true, leading to an additional X calls for each ticker for the ticker to complete
# if dividends will result in 1 FMP call and 2 more finnhub calls

# DIVIDEND HISTORY SECTION
# stock details requiring further calculations and use of lower request limit FMP API

print("7")
# no api calls required
db_stocks_with_dividends_but_never_updated = grab_list_of_never_updated_dividend_stocks_from_db(connection)
print(f"Never updated stocks to update: {db_stocks_with_dividends_but_never_updated}")


for ticker in db_stocks_with_dividends_but_never_updated:
  api_call_counts = single_ticker_api_and_update_process(ticker)
  fmp_api_call_count += api_call_counts["fmp_api_call_count"]
  finnhub_api_call_count += api_call_counts["finnhub_api_call_count"]


# if all stocks have been assessed div or no div, and api calls remain begin periodic review of previously assessed stocks

review_mode = False

if review_mode == True:
  date_ascending_db_tickers_full_stock_table = grab_all_db_data_ascending_bgy_date(connection)
  stocks_up_for_periodic_review_and_update = get_previously_updated_annual_financials_and_for_review(date_ascending_db_tickers_full_stock_table)

  for ticker in stocks_up_for_periodic_review_and_update:
    api_call_counts = single_ticker_api_and_update_process(ticker)
    fmp_api_call_count += api_call_counts["fmp_api_call_count"]
    finnhub_api_call_count += api_call_counts["finnhub_api_call_count"]


print(f"finnhub api call count: {finnhub_api_call_count}")
print(f"fmp api call count: {fmp_api_call_count}")

# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
connection.commit()
# close the cursor
cur.close()