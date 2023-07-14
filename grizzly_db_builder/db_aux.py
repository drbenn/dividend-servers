def determine_if_dividend_payer_from_annual_financials(annual_financials) -> bool:
  if annual_financials == None or annual_financials["data"] == None or len(annual_financials["data"]) == 0:
    return False
  elif len(annual_financials["data"]) > 0:
    cashflow_statement = annual_financials["data"][0]["report"]["cf"]
    for item in cashflow_statement:
      if item == "PaymentsOfDividendsCommonStock" or item["concept"] == "us-gaap_PaymentsOfDividendsCommonStock" or item["concept"] == "PaymentsOfDividendsCommonStock":
        return True
  else:
    return False