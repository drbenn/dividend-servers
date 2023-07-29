import datetime
import json


def get_all_stock_db_data(cur) -> any:
  query = "SELECT * FROM grizzly_stocks"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  return retrieved_db_data

def get_all_stock_db_data_with_no_initial_review(cur) -> any:
  query = "SELECT * FROM grizzly_stocks WHERE has_dividend IS NULL AND payout_ratios IS NULL ORDER BY ticker"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  return retrieved_db_data

def get_stock_db_data_where_has_payout_but_has_divi_skipped(cur) -> any:
  query = "SELECT * FROM grizzly_stocks WHERE has_dividend IS NULL AND payout_ratios IS NOT NULL ORDER BY ticker"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  return retrieved_db_data


def update_db_dividend_payer_false(cur, db, is_dividend_payer, ticker):
  # if not_dividend_payer last_updated timestamp set for future use in periodic review AND financial NOT stored in database
  todays_date = datetime.date.today()
  string_date = todays_date.strftime("%m-%d-%y")
  sql = "UPDATE grizzly_stocks SET has_dividend = %s, last_updated = %s WHERE ticker = %s"
  val = (is_dividend_payer, string_date, ticker)
  cur.execute(sql, val)
  db.commit()
  return

def update_db_dividend_payer_true(cur, db, is_dividend_payer, ticker):
  sql = "UPDATE grizzly_stocks SET has_dividend = %s WHERE ticker = %s"
  val = (is_dividend_payer, ticker)
  cur.execute(sql, val)
  db.commit()
  return


def update_db_calculations_and_historic_dividends(cur, db, historic_dividends, annual_dividends, years_dividend_growth, dividend_payment_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker):
  string_historic_dividends = json.dumps(historic_dividends) # dumps is json to string, loads is opposite
  string_annual_dividends = json.dumps(annual_dividends) # dumps is json to string, loads is opposite
  string_div_pay_months_and_count = json.dumps(dividend_payment_months_and_count) # dumps is json to string, loads is opposite
  sql = "UPDATE grizzly_stocks SET historic_dividends = %s, annual_dividends = %s, years_dividend_growth = %s, dividend_payment_months_and_count = %s, growth_all_years_of_history = %s, dividend_yield = %s,three_year_cagr = %s, five_year_cagr = %s WHERE ticker = %s"
  val = (string_historic_dividends, string_annual_dividends, years_dividend_growth, string_div_pay_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker)
  cur.execute(sql, val)
  db.commit()
  return


def update_db_with_profile_basics_payouts(cur, db, profile_data, basic_financials_data, annual_payout_ratios, ticker):
  todays_date = datetime.date.today()
  string_date = todays_date.strftime("%m-%d-%y")
  industry = "N/A"
  website = "N/A"
  logo = "N/A"
  if len(profile_data) > 2:
    industry = profile_data[0]
    website = profile_data[1]
    logo = profile_data[2]

  json_basic_financials = basic_financials_data[0] # TOO BIG - DO WITHOUT
  year_high = basic_financials_data[1]
  year_low = basic_financials_data[2]
  beta = basic_financials_data[3]
  # print("---------------------------SHAZAM")
  # print(json_basic_financials)


  json_annual_payout_ratios = json.dumps(annual_payout_ratios)
  sql = "UPDATE grizzly_stocks SET has_dividend = %s, industry = %s, website = %s, logo = %s, year_price_high = %s, year_price_low = %s, beta = %s, payout_ratios = %s, last_updated = %s WHERE ticker = %s"
  val = (True, industry, website, logo, year_high, year_low, beta, json_annual_payout_ratios, string_date, ticker)
  cur.execute(sql, val)
  db.commit()
  return




def add_event_to_run_log(cur, db, message):
  todays_date = datetime.date.today()
  string_date = todays_date.strftime("%m-%d-%y")
  sql = "INSERT INTO grizzly_run_log (time_stamp, summary) values (%s, %s)"
  val = (string_date, message)
  cur.execute(sql, val)
  db.commit()
  return