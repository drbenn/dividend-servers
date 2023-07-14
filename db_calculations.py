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
  



def build_annual_payout_ratios(annual_financials, annual_dividends):
  annual_payout_ratios = []
  print(annual_dividends)
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