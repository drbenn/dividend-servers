from api_keys import FINNHUB_API_KEY, FMP_API_KEY
import finnhub
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


def get_company_profile():
  finnhub_company_profile = finnhub_client.company_profile2(symbol="LRGE")
  print("RUN")
  print(finnhub_company_profile)
  # industry = finnhub_company_profile["finnhubIndustry"]
  # website = finnhub_company_profile["weburl"]
  # logo = finnhub_company_profile["logo"]
  # company_profile = {
  #     "industry": industry,
  #     "website": website,
  #     "logo": logo
  # }


get_company_profile()

print('YOLOLO')