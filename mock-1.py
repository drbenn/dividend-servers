import requests
import json
import csv
import finnhub
from api_keys import FINNHUB_API_KEY

# https://stackoverflow.com/questions/49723988/alphavantage-list-of-all-tickers-on-an-exchange
# https://github.com/rreichel3/US-Stock-Symbols
# https://finnhub.io/
# https://polygon.io/pricing
# https://www.alphavantage.co/documentation/

print("Program Started")

activeTickers = []
def getActiveTickers():
  # finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
  finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
  finnhub_stock_listing = finnhub_client.stock_symbols('US')
  # print(finnhub_stock_listing)
  # print(finnhub_client.stock_symbols('US'))
  # with open(finnhub_stock_listing) as data_file:
  #   data = json.load(data_file)
  for item in finnhub_stock_listing:
    # print(v.keys())
    #   print(v['x'], v['y'], v['yr'])
    # # print(row[0])
    # print(v)

    # print(item['symbol'])
    # print(item['description'])

    activeTickers.append(
      {
        "ticker": item['symbol'], 
        "title": item['description']
      }
    )


# def getActiveTickers():
#   with open("./assets/json/listing_status-6-19-23.csv", 'r') as file:
#     csvreader = csv.reader(file)
#     for row in csvreader:
#       # print(row[0])
#       activeTickers.append(
#         {
#          "ticker": row[0], 
#          "status": row[-1]
#         }
#       )


getActiveTickers()

print(activeTickers)
# response_API = requests.get('https://api.covid19india.org/state_district_wise.json')
# #print(response_API.status_code)
# data = response_API.text
# parse_json = json.loads(data)
# print("DATA")
# print(data)
# print("PARSE JSON")
# print(parse_json)
# active_case = parse_json['Andaman and Nicobar Islands']['districtData']['South Andaman']['active']
# print("Active cases in South Andaman:", active_case)


