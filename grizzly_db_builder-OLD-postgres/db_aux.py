def determine_if_dividend_payer_from_annual_financials(annual_financials) -> bool:
  if annual_financials == None or annual_financials["data"] == None or len(annual_financials["data"]) == 0:
    return False
  elif len(annual_financials["data"]) > 0:
    # print(annual_financials["data"][0]["report"]["cf"])
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
      if type(item) == dict:
        if item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock" or item["concept"] == "us-gaap_PaymentsOfOrdinaryDividends" or item["concept"] == "us-gaap_PaymentsOfDividends" or item["concept"] == "PaymentsOfDistributionsToAffiliates":
          return True
      elif type(item) == str:
        if item == "PaymentsOfDividendsCommonStock":
          return True
  else:

    return False
