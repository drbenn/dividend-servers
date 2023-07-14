import psycopg2
import datetime
import json

connection = psycopg2.connect(
  host="localhost",
  database="NewDB",
  user="postgres",
  password="postgres",
  port="5432"
  )


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

def get_historic_dividends_and_financials_from_db(ticker):
  query = "SELECT annual_dividends, historic_annual_financials FROM grizzly_stocks WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (ticker,))
  data = cur.fetchall()
  cur.close()
  return data

def update_db_with_payout_ratio_dictionary(annual_payout_ratios, ticker):
  json_payouts = json.dumps(annual_payout_ratios)
  cur = connection.cursor()
  query = "UPDATE grizzly_stocks SET payout_ratios = %s, last_updated = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, [json_payouts, datetime.datetime.now(), ticker])
  connection.commit()
  cur.close()
  return

def update_company_profile(industry, website, logo, ticker):
  query = "UPDATE grizzly_stocks SET industry = %s, website = %s, logo = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (industry, website, logo, ticker))
  connection.commit()
  cur.close()
  return

def update_basic_financials(json_basic_financials, year_high, year_low, beta, ticker):
  query = "UPDATE grizzly_stocks SET basic_financials = %s, year_price_high = %s, year_price_low = %s, beta = %s WHERE ticker = %s"
  cur = connection.cursor()
  cur.execute(query, (json_basic_financials, year_high, year_low, beta, ticker))
  connection.commit()
  cur.close()
  return

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