import psycopg2
import datetime
import json



def add_event_to_run_log(connection, message):
  cur = connection.cursor()
  cur.execute("INSERT INTO grizzly_run_log (time_stamp, summary) values (%s, %s)", (datetime.datetime.now(), message))
  connection.commit()
  cur.close()


def grab_all_db_data(connection) -> any:
  cur = connection.cursor()
  query = "SELECT * FROM grizzly_stocks"
  cur.execute(query)
  retrieved_db_data = cur.fetchall()
  cur.close()
  return retrieved_db_data


def insert_new_tickers_to_db(connection, tickers_to_add_to_db, all_current_us_tickers) -> any:
  for ticker in tickers_to_add_to_db:
    for ticker_info in all_current_us_tickers:
      if ticker == ticker_info["symbol"]: 
        cur = connection.cursor()
        cur.execute("INSERT INTO grizzly_stocks (ticker, name, equity_type) values (%s, %s, %s)", (ticker_info["symbol"], ticker_info["description"], ticker_info["type"]))
        connection.commit()
        cur.close()


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
  return tickers_to_update


def update_db_with_annual_financials(connection, ticker, is_dividend_payer, annual_financials) -> any:
  if is_dividend_payer == True:
    update_db_dividend_payer_true(connection, annual_financials, is_dividend_payer, ticker)
  elif is_dividend_payer == False:
    update_db_dividend_payer_false(is_dividend_payer, ticker)


def update_db_dividend_payer_true(connection, annual_financials, is_dividend_payer, ticker):
  json_financials = json.dumps(annual_financials)
  query = "UPDATE grizzly_stocks SET historic_annual_financials = %s, has_dividend = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_financials, is_dividend_payer, ticker])
  connection.commit()
  cur.close()


def update_db_dividend_payer_false(connection, is_dividend_payer, ticker):
  # if not_dividend_payer last_updated timestamp set for future use in periodic review AND financial NOT stored in database
  query = "UPDATE grizzly_stocks SET has_dividend = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [is_dividend_payer, datetime.datetime.now(), ticker])
  connection.commit()
  cur.close()


def get_historic_dividends_and_financials_from_db(connection, ticker):
  query = "SELECT annual_dividends, historic_annual_financials FROM grizzly_stocks WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (ticker,))
  data = cur.fetchall()
  cur.close()
  return data


def update_db_with_payout_ratio_dictionary(connection, annual_payout_ratios, ticker):
  json_payouts = json.dumps(annual_payout_ratios)
  cur = connection.cursor()
  query = "UPDATE grizzly_stocks SET payout_ratios = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_payouts, datetime.datetime.now(), ticker])
  connection.commit()
  cur.close()
  return


def update_company_profile(connection, industry, website, logo, ticker):
  query = "UPDATE grizzly_stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (industry, website, logo, ticker))
  connection.commit()
  cur.close()
  return


def update_basic_financials(connection, json_basic_financials, year_high, year_low, beta, ticker):
  query = "UPDATE grizzly_stocks SET basic_financials = %s, year_price_high = %s, year_price_low = %s, beta = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (json_basic_financials, year_high, year_low, beta, ticker))
  connection.commit()
  cur.close()
  return


def update_db_calculations_and_historic_dividends(connection, historic_dividends, annual_dividends, years_dividend_growth, dividend_payment_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker):
  json_historic_dividends = json.dumps(historic_dividends)
  json_annual_dividends = json.dumps(annual_dividends)
  json_div_pay_months_and_count = json.dumps(dividend_payment_months_and_count)
  query = "UPDATE grizzly_stocks SET historic_dividends = %s, annual_dividends = %s, years_dividend_growth = %s, dividend_payment_months_and_count = %s, growth_all_years_of_history = %s, dividend_yield = %s,three_year_cagr = %s, five_year_cagr = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_historic_dividends, json_annual_dividends, years_dividend_growth, json_div_pay_months_and_count, growth_all_years_of_history, current_dividend_yield, three_year_cagr, five_year_cagr, ticker])
  connection.commit()
  cur.close()


# def grab_db_data_tickers_previously_updated_with_has_dividends(connection) -> any:
#   cur = connection.cursor()
#   # query = "SELECT * FROM stocks WHERE has_dividend = True OR has_dividend = False ORDER BY last_updated ASC"
#   query = "SELECT ticker,last_updated FROM grizzly_stocks WHERE has_dividend = True ORDER BY last_updated ASC"
#   cur.execute(query)
#   retrieved_db_data = cur.fetchall()
#   cur.close()
#   tickers_to_update = []
#   for item in retrieved_db_data:
#     if item[1] == None:
#       tickers_to_update.append(item[0])
#   return tickers_to_update