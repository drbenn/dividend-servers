https://dev.to/lordghostx/how-to-host-flask-applications-on-namecheap-cpanel-299b

https://www.youtube.com/watch?v=qfYzCdkVwig
pip install Flask-MySQLdb
pip install -U flask-cors
pip install schedule
pip install psycopg2


<!-- https://finnhub.io/ -->
<!-- https://www.alphavantage.co/documentation/ --> - up to 5 API requests per minute and 500 requests per day
<!-- https://site.financialmodelingprep.com/developer/docs/ --> - up to 250 requests/day

# https://stackoverflow.com/questions/49723988/alphavantage-list-of-all-tickers-on-an-exchange
# https://github.com/rreichel3/US-Stock-Symbols
# https://finnhub.io/
# https://polygon.io/pricing
# https://www.alphavantage.co/documentation/



# CREATE TABLE grizzly_stocks (
# 	ticker VARCHAR PRIMARY KEY,
# 	last_updated TIMESTAMP WITH TIME ZONE,
# 	name VARCHAR ( 75 ),
# 	equity_type VARCHAR ( 15 ),
#  	has_dividend BOOLEAN,
# 	industry VARCHAR ( 75 ),
# 	website VARCHAR ( 100 ),
# 	logo VARCHAR ( 100 ),
# 	dividend_yield NUMERIC,
# 	years_dividend_growth NUMERIC,
# 	growth_all_years_of_history BOOLEAN,
# 	payout_ratios JSONB,
# 	three_year_cagr NUMERIC,
# 	five_year_cagr NUMERIC,
# 	year_price_high NUMERIC,
# 	year_price_low NUMERIC,
# 	beta NUMERIC,
# 	backup_stock_price NUMERIC,
# 	backup_stock_price_date_saved TIMESTAMP WITH TIME ZONE,
# 	dividend_payment_months_and_count JSONB,
# 	annual_dividends JSONB,
# 	historic_dividends JSONB,
# 	basic_financial_metrics JSONB,
# 	quarterly_financials JSONB,
# 	historic_annual_financials JSONB,
# 	basic_financials JSONB
# );


# CREATE TABLE grizzly_users (
# 	username VARCHAR ( 50 ) PRIMARY KEY,
# 	email VARCHAR ( 50 ) ,
# 	password VARCHAR ( 50 ),
# 	join_date TIMESTAMP WITH TIME ZONE,
#   portfolios JSONB
# );

# CREATE TABLE grizzly_portfolios (
# 	username VARCHAR ( 50 ) PRIMARY KEY,
# 	portfolios JSONB
# );


# CREATE TABLE grizzly_run_log (
# 	time_stamp TIMESTAMP WITH TIME ZONE,
# 	summary VARCHAR ( 100 )
# );

# NAMECHEAP HOSTING
* https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi_rb_qn4SAAxWPKlkFHV-nCksQFnoECBoQAQ&url=https%3A%2F%2Fwww.namecheap.com%2Fsupport%2Fknowledgebase%2Farticle.aspx%2F10048%2F2182%2Fhow-to-work-with-python-app%2F&usg=AOvVaw39kwn3CXhqjBE3YKbksZbI&opi=89978449

* https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi_rb_qn4SAAxWPKlkFHV-nCksQFnoECCcQAQ&url=https%3A%2F%2Fwww.namecheap.com%2Fsupport%2Fknowledgebase%2Farticle.aspx%2F9587%2F29%2Fhow-to-run-python-scripts%2F&usg=AOvVaw0XEYSO6nsXopt3gXHIsq-w&opi=89978449

* https://devpress.csdn.net/cicd/62ec375619c509286f416824.html

* https://www.youtube.com/watch?v=IBfj_0Zf2Mo

* 1. create app
* 2. stop app
* 3. go to file manager and overwrite app.py and also upload requirements.txt in same directory
* 4. Go to python app, in configuration files type in requirements.txt and add

* create requirements with pip freeze > requirements.txt in terminal
