import mysql.connector
import datetime
import time

import db_fin_api_calls
import db_actions
import db_helpers

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="pass",
  database="grizzly"
)

cur = db.cursor()

todays_date = datetime.date.today()
string_date = todays_date.strftime("%m-%d-%y")


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
  # "quarterly_financials": 23,
  # "historic_annual_financials": 24,
  "basic_financials": 23
}



#CHARACTERS = TINYTEXT = 255, TEXT = 65,535, MEDUIMTEXT = 16,777,215, LONGTEXT = 4,294,967,295
# LONGTEXT
#TIMESTAMP https://www.w3resource.com/mysql/date-and-time-functions/mysql-timestamp-function.php
# cur.execute("CREATE DATABASE grizzly")
# DATE is formatted 'YYYY-MM-DD'
# cur.execute("CREATE TABLE grizzly_users(username VARCHAR(50), email VARCHAR(50), password VARCHAR(50), join_date VARCHAR(15), portfolios TEXT, userID INT AUTO_INCREMENT, PRIMARY KEY (userID))")
# cur.execute("CREATE TABLE grizzly_run_log(time_stamp VARCHAR(50), summary TINYTEXT)")
# cur.execute("CREATE TABLE grizzly_stocks(ticker VARCHAR(7), last_updated VARCHAR(15), name VARCHAR(75), equity_type VARCHAR(15), has_dividend BOOLEAN, industry VARCHAR(75), website VARCHAR(100), logo VARCHAR(100), dividend_yield FLOAT, years_dividend_growth TINYINT, growth_all_years_of_history BOOLEAN, payout_ratios TEXT, three_year_cagr FLOAT, five_year_cagr FLOAT, year_price_high FLOAT, year_price_low FLOAT, beta FLOAT, backup_stock_price FLOAT, backup_stock_price_date_saved VARCHAR(15), dividend_payment_months_and_count TINYTEXT, annual_dividends TEXT, historic_dividends TEXT, basic_financial_metrics TEXT, basic_financials TEXT)")

# print("TABLE CREATED")


def update_db_with_historic_dividends_and_related_calculations_and_return_annual_dividends(historic_dividends, ticker) -> any:
  print(historic_dividends)
  print("JUNK")
  print(type(historic_dividends))
  dividend_history = historic_dividends["historical"]
  payment_date_string = None
  if "paymentDate" in dividend_history[0].keys():
    payment_date_string = "paymentDate"
  elif "payment_date" in dividend_history[0].keys():
    payment_date_string = "payment_date"

  # print(historic_dividends)
  annual_dividends = db_helpers.combine_dividends_into_annual_dividends(historic_dividends, payment_date_string)
  print(annual_dividends)
  years_dividend_growth = db_helpers.get_consistent_years_dividend_growth(annual_dividends)
  dividend_payment_months_and_count = db_helpers.get_payment_months_and_count(historic_dividends)
  growth_all_years_of_history = len(annual_dividends) == years_dividend_growth
  current_dividend_yield = db_helpers.calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_count)
  three_year_cagr = db_helpers.calculate_x_year_cagr(annual_dividends, 3)
  five_year_cagr = db_helpers.calculate_x_year_cagr(annual_dividends, 5)
  db_actions.update_db_calculations_and_historic_dividends(cur, db, historic_dividends, annual_dividends, years_dividend_growth, dividend_payment_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker)
  return annual_dividends


def has_dividend_and_update_db_only(tickers):
  forCount = 0
  lgt = len(tickers)

  for ticker in tickers:
    annual_financials = db_fin_api_calls.get_annual_financials(ticker)
    forCount += 1
    if annual_financials == "No Financials Available":
      db_actions.update_db_dividend_payer_false(cur, db, False, ticker)
      time.sleep(3)
      continue
    else:
      # print(f"----------------{ticker} ANNUAL FINANCIALS ----------------------") 
      # print(annual_financials)
      is_dividend_payer = db_helpers.determine_if_dividend_payer_from_annual_financials(annual_financials)
      print(f"{forCount}/{lgt}- {ticker} is a dividend payer?: {is_dividend_payer}")

      if is_dividend_payer != True:
        db_actions.update_db_dividend_payer_false(cur, db, False, ticker)
        time.sleep(3)
        # print(f"{forCount}/{lgt} -{ticker} Not Dividend Payer")
        continue
      if is_dividend_payer == True:
        db_actions.update_db_dividend_payer_true(cur, db, True, ticker)
        time.sleep(3)
        # print(f"{forCount}/{lgt} - IS DIVIDEDEND PAYER - {ticker} @ {datetime.datetime.now()}")
    


def full_scope_ticker_update(tickers):
  forCount = 1
  fmp_api_calls = 0
  fmp_call_limit = 250
  lgt = len(tickers)

  for ticker in tickers:
    annual_financials = db_fin_api_calls.get_annual_financials(ticker)

    if annual_financials == "No Financials Available":
      db_actions.update_db_dividend_payer_false(cur, db, False, ticker)
      time.sleep(3)
      continue
    else:
      print(f"----------------{ticker} ANNUAL FINANCIALS ----------------------") 
      # print(annual_financials)
      is_dividend_payer = db_helpers.determine_if_dividend_payer_from_annual_financials(annual_financials)
      print(f"{forCount}/{lgt}- {ticker} is a dividend payer?: {is_dividend_payer}")

      if is_dividend_payer != True:
        db_actions.update_db_dividend_payer_false(cur, db, False, ticker)
        time.sleep(3)
        print(f"{ticker} Not Dividend Payer")
        continue
      elif fmp_api_calls <= fmp_call_limit: # Does have dividends
        historic_dividends = db_fin_api_calls.get_historic_dividends_from_fmp(ticker)
        fmp_api_calls += 1
        if historic_dividends == "No dividend history" or historic_dividends == None or historic_dividends["historical"] == None or historic_dividends["historical"] == [] or len(historic_dividends["historical"]) == 0: # Although dividends in Annual Statement, sometimes FMP does not have dividend history
          db_actions.update_db_dividend_payer_false(cur, db, False, ticker)
          time.sleep(3)
          continue
        else:
          print(historic_dividends)
          time.sleep(3) # Delay to prevent API overload
          annual_dividends = update_db_with_historic_dividends_and_related_calculations_and_return_annual_dividends(historic_dividends, ticker)
          profile_data = db_fin_api_calls.get_company_profile_and_related_data(ticker) # 1 finnhub API call
          time.sleep(3) # Delay to prevent API overload
          basic_financials_data = db_fin_api_calls.get_basic_financials_hi_low_beta(ticker) # 1 finnhub API call
          time.sleep(3) # Delay to prevent API overload
          annual_payout_ratios = db_helpers.calculate_payout_ratios(annual_financials, annual_dividends, ticker) # No API call
          db_actions.update_db_with_profile_basics_payouts(cur, db, profile_data, basic_financials_data, annual_payout_ratios, ticker) 
          db_actions.add_event_to_run_log(cur, db, f"{ticker} individual stock information updated")
          print(f"{forCount}/X - Completed update single stock data of {ticker} @ {datetime.datetime.now()}")
    forCount += 1


# def get_and_insert_all_us_tickers():
#   all_current_us_tickers = db_fin_api_calls.get_all_us_tickers()
#   print(all_current_us_tickers)
#   for item in all_current_us_tickers:
#     sql = "INSERT INTO grizzly_stocks (ticker, name, equity_type) VALUES (%s, %s, %s)"
#     val = (item["symbol"], item["description"], item["type"])
#     cur.execute(sql, val)
#     db.commit()

# get_and_insert_all_us_tickers()

# TODO: For future, query db for existing and compare before adding
# def update_all_us_tickers:


def db_stocks_to_tickers(db_stocks) -> any:
  print("IN HERE")
  tickers_eligible_for_update = 0
  eligible_tickers = []

  for item in db_stocks:
      eligible_tickers.append(item[db_schema['ticker']])
      tickers_eligible_for_update += 1 
  return eligible_tickers

def update_stock_info_if_uninvestigated():
  # all_db_data = db_actions.get_all_stock_db_data_with_no_initial_review(cur)
  db_has_div_no_fmp = db_actions.get_all_stock_db_data_with_has_div_but_no_addtl_info(cur)
  print(len(db_has_div_no_fmp))
  # print(all_db_data)
  # print("DATA GOT")
  tickers_to_check = db_stocks_to_tickers(db_has_div_no_fmp)
  print(tickers_to_check)
  latest = tickers_to_check.index("FTAI") + 1
  print(tickers_to_check[latest:])
  # latest = tickers_to_check.index("EWTX")
  # print(tickers_to_check[latest:])


  # shortenend_tickers = tickers_to_check[latest:]
  full_scope_ticker_update(tickers_to_check[latest:])




def update_has_dividend_only_bc_fmp_exhausted():
  all_db_data = db_actions.get_all_stock_db_data_with_no_initial_review(cur)
  # print(all_db_data)
  # print("DATA GOT")
  tickers_to_check = db_stocks_to_tickers(all_db_data)
  print(tickers_to_check)
  # latest = tickers_to_check.index("EWTX")
  # print(tickers_to_check[latest:])


  # shortenend_tickers = tickers_to_check[latest:]
  has_dividend_and_update_db_only(tickers_to_check)



# def update_missed_stocks_with_has_dividend():
#   missed_stocks = db_actions.get_stock_db_data_where_has_payout_but_has_divi_skipped(cur)
#   tickers_to_check = db_stocks_to_tickers(missed_stocks)
#   print(tickers_to_check)
#   print(len(tickers_to_check))
#   for ticker in tickers_to_check:
#     db_actions.update_db_dividend_payer_true(cur, db, True, ticker)

# update_missed_stocks_with_has_dividend()




# FULL SCOPE ON HAS_DIVIDEND TRUE BUT NOTHING ELSE
update_stock_info_if_uninvestigated()

# ONLY HAS DIVIDEND
# update_has_dividend_only_bc_fmp_exhausted()







