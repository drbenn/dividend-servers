# import psycopg2

# conn = psycopg2.connect(database="db_name",
#                         host="db_host",
#                         user="db_user",
#                         password="db_pass",
#                         port="db_port")

# cursor = conn.cursor()


# import psycopg2

# def connect_to_database():
#   """Connects to the PostgreSQL database."""
#   connection = psycopg2.connect(
#       database="NewDB",
#       user="postgres",
#       password="postgres",
#       host="localhost",
#       port="5432")
#   return connection

# def post_data_to_table(connection, time, randomInt):
#   """Posts data to the PostgreSQL table."""
#   cursor = connection.cursor()
#   query = """
#     INSERT INTO timestamp (time, randomInt)
#     VALUES (%s, %s)
#   """
#   cursor.execute(query, (time, randomInt))
#   connection.commit()
#   cursor.close()

# def get_all_table_data(connection):
#   """Gets all data from the PostgreSQL table."""
#   cursor = connection.cursor()
#   query = """
#     SELECT *
#     FROM timestamp
#   """
#   cursor.execute(query)
#   data = cursor.fetchall()
#   cursor.close()
#   return data

# if __name__ == "__main__":
#   connection = connect_to_database()
#   post_data_to_table(connection, "Billy", 5)
#   data = get_all_table_data(connection)
#   print(data)



import psycopg2
import finnhub
from psycopg2.extras import Json
from api_keys import FINNHUB_API_KEY


con = psycopg2.connect(
    host="localhost",
    database="NewDB",
    user="postgres",
    password="postgres",
    port="5432")

#cursor
cur = con.cursor()


def get_current_stock_price(symbol):
  finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
  quote_response = finnhub_client.quote(symbol)
  current_price = quote_response["c"]
  percent_change = quote_response["dp"]
  previous_close = quote_response["pc"]
  print([quote_response])
  # print(quote_response, current_price, percent_change, previous_close)
  # print('current price: ', current_price, 'percent change: ', percent_change, 'previous close: ', previous_close)
  cur.execute("insert into persons (personid, fullname, jsontest) values (%s, %s, %s)", (10, 'Big Bill', Json(quote_response)))


get_current_stock_price("msft")

# cur.execute("insert into persons (personid, fullname) values (%s, %s)", (2, 'Johny'))

cur.execute("select * from persons")
rows = cur.fetchall()

for r in rows:
  print(f"id: {r[0]}, name {r[1]}, json {r[2]}")

# must commit transaction/changes when inserting(& deleting?). Commit not needed for get
con.commit()
# close the cursor
cur.close()




# close the connection
con.close()



# def post_data_to_table(connection, time, randomInt):
#   """Posts data to the PostgreSQL table."""
#   cursor = connection.cursor()
#   query = """
#     INSERT INTO timestamp (time, randomInt)
#     VALUES (%s, %s)
#   """
#   cursor.execute(query, (time, randomInt))
#   connection.commit()
#   cursor.close()

# def get_all_table_data(connection):
#   """Gets all data from the PostgreSQL table."""
#   cursor = connection.cursor()
#   query = """
#     SELECT *
#     FROM timestamp
#   """
#   cursor.execute(query)
#   data = cursor.fetchall()
#   cursor.close()
#   return data

# if __name__ == "__main__":
#   connection = connect_to_database()
#   post_data_to_table(connection, "Billy", 5)
#   data = get_all_table_data(connection)
#   print(data)