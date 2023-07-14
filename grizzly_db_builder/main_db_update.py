import datetime
import time
import schedule
from schedule import repeat, every
import psycopg2

import db_calls
import db_calculations
import db_aux
import db_fin_calls


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


NEVER_UPDATED_CYCLE_ROW_LIMIT = 18000
FMP_API_DAILY_CALL_LIMIT = 10

# ------------------------------------------------------------------------------
# ------------------------------   DB_SCHEMA FUNCTIONS  ------------------------
# ------------------------------------------------------------------------------


def find_tickers_to_add(all_current_us_tickers, all_db_data_no_updates) -> list[str]:
  stocks_already_in_db = []
  for line in all_db_data_no_updates:
    stocks_already_in_db.append(line[db_schema["ticker"]])
  tickers_to_add_to_db = []
  for stock in all_current_us_tickers:
    if stock["symbol"] not in stocks_already_in_db:
      tickers_to_add_to_db.append(stock["symbol"])
  return tickers_to_add_to_db


def get_never_updated_annual_financials_and_determine_if_dividends(db_stocks) -> any:
  tickers_eligible_for_update = 0
  eligible_ticker_dicts = []

  for item in db_stocks:
    if item[db_schema["has_dividend"]] == None and tickers_eligible_for_update <= NEVER_UPDATED_CYCLE_ROW_LIMIT:
      eligible_ticker_dicts.append(item)
      tickers_eligible_for_update += 1 

  for index, item in enumerate(eligible_ticker_dicts):
    ticker = item[db_schema['ticker']]
    annual_financials = db_fin_calls.get_annual_financials(connection, ticker)
    is_dividend_payer = db_aux.determine_if_dividend_payer_from_annual_financials(annual_financials)
    print(f"{index + 1} of {NEVER_UPDATED_CYCLE_ROW_LIMIT} - {ticker} is a dividend payer?: {is_dividend_payer}")
    db_calls.update_db_with_annual_financials(connection, ticker, is_dividend_payer, annual_financials)
    return


def update_db_with_historic_dividends_and_related_calculations(connection, historic_dividends, ticker) -> any:
  print(historic_dividends)
  dividend_history = historic_dividends["historical"]
  payment_date_string = None
  if "paymentDate" in dividend_history[0].keys():
    payment_date_string = "paymentDate"
  elif "payment_date" in dividend_history[0].keys():
    payment_date_string = "payment_date"
  if len(dividend_history) == 0:
    # if not_dividend_payer last_updated timestamp set to catch for periodic review AND financial NOT stored in database
    db_calls.update_db_dividend_payer_false(connection, False, ticker)
    return
  else:
    print(historic_dividends)
    annual_dividends = db_calculations.combine_dividends_into_annual_dividends(historic_dividends, payment_date_string)
    years_dividend_growth = db_calculations.get_consistent_years_dividend_growth(annual_dividends)
    dividend_payment_months_and_count = db_calculations.get_payment_months_and_count(historic_dividends)
    growth_all_years_of_history = len(annual_dividends) == years_dividend_growth
    current_dividend_yield = db_calculations.calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_count)
    three_year_cagr = db_calculations.calculate_x_year_cagr(annual_dividends, 3)
    five_year_cagr = db_calculations.calculate_x_year_cagr(annual_dividends, 5)
    db_calls.update_db_calculations_and_historic_dividends(connection, historic_dividends, annual_dividends, years_dividend_growth, dividend_payment_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker)



# ------------------------------------------------------------------------------
# ---------------------  MAIN OPERATIONS/TASKS SCHEDULING   --------------------
# ------------------------------------------------------------------------------

@repeat(every().day.at('11:07:00'))
def update_full_us_stock_listing():
  print(f"Running task 1 of 3 'update_full_us_stock_listing' @ {datetime.datetime.now()}")
  all_current_us_tickers = db_fin_calls.get_all_us_tickers()
  all_db_data = db_calls.grab_all_db_data(connection)
  tickers_to_add_to_db = db_aux.find_tickers_to_add(all_current_us_tickers, all_db_data)
  db_calls.insert_new_tickers_to_db(connection, tickers_to_add_to_db, all_current_us_tickers)
  db_calls.add_event_to_run_log(connection, "Daily stock listing verified and updated")
  print(f"Completed task 1 of 3 'update_full_us_stock_listing' @ {datetime.datetime.now()}")


@repeat(every().day.at('20:33:40'))
def determine_if_never_updated_ticker_has_dividends_on_annual_financials():
  print(f"Running task 2 of 3 'determine_if_ticker_has_dividends_financials' @ {datetime.datetime.now()}")
  all_db_data = db_calls.grab_all_db_data(connection)
  get_never_updated_annual_financials_and_determine_if_dividends(all_db_data)
  db_calls.add_event_to_run_log(connection, "Daily stock_has_dividened updated")
  print(f"Completed task 2 of 3 'determine_if_ticker_has_dividends_financials' @ {datetime.datetime.now()}")


@repeat(every().day.at('13:41:25'))
def update_individual_dividend_stock_data():
  new_tickers_to_update = db_calls.grab_db_data_tickers_never_updated_with_has_dividends(connection) 
  print(new_tickers_to_update)
  tickers = new_tickers_to_update[:250]

  for ticker in tickers:
    print(f"Running task 3 of 3 update single stock data of {ticker} @ {datetime.datetime.now()}")
    historic_dividends = db_fin_calls.get_historic_dividends_from_fmp(connection, ticker)
    if historic_dividends == None: # Although dividends in Annual Statement, sometimes FMP does not have dividend history
      db_calls.update_db_dividend_payer_false(connection, False, ticker)
      continue
    else:  
      time.sleep(3) # Delay to prevent FMP API overload
      update_db_with_historic_dividends_and_related_calculations(connection, historic_dividends, ticker)
      db_fin_calls.get_company_profiles_and_update_db(connection, ticker) # 1 finnhub API call
      db_fin_calls.get_basic_financials_hi_low_beta_and_update_db(connection, ticker) # 1 finnhub API call
      db_calculations.calculate_payout_ratios_and_update_db(connection, ticker) # No API call
      db_calls.add_event_to_run_log(connection, f"{ticker} individual stock information updated")
      print(f"Completed task 3 of 3 update single stock data of {ticker} @ {datetime.datetime.now()}")


update_individual_dividend_stock_data()


while True:
  schedule.run_pending()
  time.sleep(1)