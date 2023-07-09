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
# 	join_date TIMESTAMP WITH TIME ZONE
# );

# CREATE TABLE grizzly_portfolios (
# 	username VARCHAR ( 50 ) PRIMARY KEY,
# 	portfolios JSONB
# );