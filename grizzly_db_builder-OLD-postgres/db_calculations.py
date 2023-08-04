import datetime
import calendar

import db_calculations
import db_calls
import db_fin_calls


def get_consistent_years_dividend_growth(annual_dividends) -> int:
  list_len = len(annual_dividends)
  if list_len == 0:
    return
  if list_len == 1:
    annual_dividends = [annual_dividends]
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
  

def build_annual_payout_ratios(annual_financials, annual_dividends, ticker):
  annual_payout_ratios = []
  if "data" not in annual_financials:
    return[]
  else:
    for annual in annual_financials["data"]:
      if any(dictionary.get("year") == annual["year"] for dictionary in annual_dividends):
        annual_dividend_dictionary = None
        for dividend_dict in annual_dividends:
          if dividend_dict["year"] == annual["year"]:
            annual_dividend_dictionary = dividend_dict

        annual_dividend_paid = float(annual_dividend_dictionary["total_annual_dividend"])
        income_statement = annual["report"]["ic"]
        eps_for_year = None

        for item in income_statement:
          if item["concept"] == "us-gaap_EarningsPerShareBasic":
            eps_for_year = float(item["value"])

        if annual_dividend_paid and eps_for_year:
          payout_ratio = round((annual_dividend_paid / eps_for_year) , 6)
          annual_payout_ratios.append({ "year": annual["year"], "payout_ratio": payout_ratio, "eps": eps_for_year}) 
    return annual_payout_ratios


def calculate_x_year_cagr(annual_dividends, years) -> float:
  if len(annual_dividends) >= years + 2:
    beginning_balance = float(annual_dividends[years + 1]["total_annual_dividend"])
    ending_balance = float(annual_dividends[1]["total_annual_dividend"]) # most recent year with all dividends
    cagr = round(float(((ending_balance / beginning_balance) ** ( 1 / years ))  - 1), 4)
    return cagr
  else:
    return 0
  

def combine_dividends_into_annual_dividends(historic_dividends, payment_date_string) -> list[object]:
  historic_dividends = historic_dividends["historical"]
  annual_dividends = []
  for payment in historic_dividends:
    # listed year of most recent payment date
    if len(payment[payment_date_string][:4]) > 0:
      payment_year = int(payment[payment_date_string][:4])
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


def calculate_payout_ratios_and_update_db(connection, ticker)  -> str:
  data = db_calls.get_historic_dividends_and_financials_from_db(connection, ticker)
  annual_dividends = data[0][0]
  annual_financials = data[0][1]["data"]
  annual_payout_ratios = db_calculations.build_annual_payout_ratios(annual_financials, annual_dividends, ticker)
  db_calls.update_db_with_payout_ratio_dictionary(connection, annual_payout_ratios, ticker)
  return


def calculate_current_dividend_yield(ticker, historic_dividends, dividend_payment_months_and_counts) -> float:
  current_quote = db_fin_calls.get_current_price_quote(ticker)
  current_price = current_quote["c"]
  if current_price == 0:
     return 0
  else:
    payments_per_year = dividend_payment_months_and_counts["ttm_dividend_payment_count"]
    ttm_dividends = 0
    for item in historic_dividends["historical"][:payments_per_year]:
      if item["dividend"] == None:
        ttm_dividends += 0
      else:
        ttm_dividends += float(item["dividend"])
    current_dividend_yield = round(float((ttm_dividends / current_price)), 4)
    return current_dividend_yield