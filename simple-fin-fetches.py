import datetime
import finnhub
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from api_keys import FINNHUB_API_KEY, FMP_API_KEY




finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


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


def get_annual_financials(ticker) -> list[object]:
  print(f"calling finnhub for annual financials and testing for dividend of {ticker} @ {datetime.datetime.now()}")
  try:
    annual_financials = finnhub_client.financials_reported(symbol=ticker, freq='annual')
    print(annual_financials)
    return annual_financials
  except Exception:
    print("Annual Financial call failed")
    


def get_historic_dividends_from_fmp(ticker) -> any:
  print(f"ticker in get historic being procesed: {ticker}")
  url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={FMP_API_KEY}"
  try:
    with urlopen(url, timeout=10) as response:
      data = response.read().decode("utf-8")
      historic_dividends = json.loads(data) # json.loads converts json string to python dictionary
      print(historic_dividends)
      return historic_dividends
  except HTTPError as error:
    print(f"FMP API CALL HTTPError for ticker {ticker}: {error.status}, {error.reason}")
    return
  except URLError as error:
    print(f"FMP API CALL URLError for ticker {ticker}: {error.reason}")
    return
  except TimeoutError:
    print(f"FMP API CALL TimeoutError: Request timed out for ticker {ticker}")
    return

  

def get_company_profiles_and_update_db(ticker) -> any:
  try:
    finnhub_company_profile = finnhub_client.company_profile2(symbol=ticker)
    industry = finnhub_company_profile["finnhubIndustry"]
    website = finnhub_company_profile["weburl"]
    logo = finnhub_company_profile["logo"]
    print(finnhub_company_profile)
    return
  except Exception:
    print("Finnhub api call failed. No company profile available.")
    return


def get_basic_financials_hi_low_beta_and_update_db(ticker) -> any:
  basic_financials = finnhub_client.company_basic_financials(ticker, 'all')
  json_basic_financials = json.dumps(basic_financials)
  year_high = float(basic_financials["metric"]["52WeekHigh"])
  year_low = float(basic_financials["metric"]["52WeekLow"])
  beta = None
  try:
    beta = float(basic_financials["metric"]["beta"])
  finally:
    print(f"ticker={ticker} , hi: {year_high}, lo: {year_low}, beta: {beta}, basic financials: {json_basic_financials}")

  

def get_current_price_quote(ticker):
  quote = finnhub_client.quote(ticker)
  return quote

TICKER = ""

get_current_price_quote(TICKER)
get_all_us_tickers()
get_company_profiles_and_update_db(TICKER)
get_historic_dividends_from_fmp(TICKER)
get_basic_financials_hi_low_beta_and_update_db(TICKER)
get_annual_financials(TICKER)