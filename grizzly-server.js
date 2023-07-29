const express = require('express');
// const { Pool } = require('pg'); // Import Pool from pg module
const cors = require('cors'); // Import the cors module
const axios = require('axios');
const mysql = require('mysql2');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "pass",
  database: "grizzly"
});
// PostgreSQL database configuration
// const pool = new Pool({
//   user: 'postgres',
//   host: 'localhost', // Default is 'localhost'
//   database: 'NewDB',
//   password: 'postgres',
//   port: 5432 // Default PostgreSQL port
// });

grizzly_users_db_schema = {
  "username": 0,
  "email": 1,
  "password": 2,
  "join_date": 3
}

data_schema = {
 "ticker": 0,
 "name": 1,
 "type": 2,
 "industry": 3,
 "website": 4,
 "logo": 5,
 "dividend_yield": 6,
 "years_dividend_growth": 7, 
 "growth_all_years_of_history": 8, 
 "payout_ratios": 9,
 "three_year_cagr": 10, 
 "five_year_cagr": 11, 
 "year_price_high": 12,
 "year_price_low": 13,
 "beta": 14,
 "backup_stock_price": 15,
 "backup_stock_price_date_saved": 16,
 "dividend_payment_months_and_count": 17,
 "annual_dividend": 18
}

// const today = new Date();
// const date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();

const MOMENT = require( 'moment' );
let date = MOMENT().format( 'YYYY-MM-DD');

app.get('/', async (req, res) => {
  try {
    // Example query to test the connection
    // const { rows } = await pool.query('SELECT NOW() AS current_time');
    // const currentTime = rows[0].current_time;
    res.send(`Hello, World! The current time is: ${date}`);
  } catch (error) {
    console.error('Error executing query:', error);
    res.status(500).send('Error');
  }
});



// def db_fetch(query):
//   print("IN DB FETCH")
//   cur = connection.cursor()
//   cur.execute(query)
//   retrieved_db_data = cur.fetchall()
//   cur.close()
//   # print("fetch returned")
//   # print(retrieved_db_data)
//   return retrieved_db_data

// def register_error_handler(retrieved_db_data, submitted_username, submitted_email):
//   # Check if username or password is unique
//   db_username_index = 0
//   db_email_index = 1
//   error_message = None
//   for user in retrieved_db_data:
//     if user[db_username_index] == submitted_username:
//       error_message = "Invalid request. Username already exists."
//       print(error_message, 400)
//       return error_message, 400
//     if user[db_email_index] == submitted_email:
//       error_message = "Invalid request. Email already exists."
//       return error_message, 400
    
// def register_new_user_in_db(username, email, password):
//   cur = connection.cursor()
//   cur.execute("INSERT INTO grizzly_users (username, email, password, join_date) values (%s, %s, %s, %s)", (username, email, password, dt.now() ))
//   connection.commit()
//   cur.close()
//   return 'User registered successfully', 200

// def authenticate_user(username, password):
//   print("IN AUTHETICATE")
//   retrieved_db_data = db_fetch(f"SELECT * from grizzly_users where username = '{username}' AND password = '{password}'")
//   print(retrieved_db_data)
//   print(len(retrieved_db_data))
//   if len(retrieved_db_data) != 1:
//     return False
//   if len(retrieved_db_data) == 1:
//     return True

// def get_user_data(username):
//   print("in get user data")
//   retrieved_db_data = db_fetch(f"SELECT portfolios from grizzly_users where username = '{username}'")


  

// def http_query_to_db_query_tickers(tickers):
//   if len(tickers) > 1:
//     db_query = ''
//     for index, item in enumerate(tickers):
//       if index == 0:
//         db_query += f"ticker = '{item}'"
//       else:
//         db_query += f" OR ticker = '{item}'"
//     return db_query
//   else:
//     return f"ticker = '{tickers[0]}'"

// def data_transform_to_dict(data):
//   data_dict_array = []
//   for item in data:
//     data_dict = {
//     "ticker": item[data_schema["ticker"]],
//     "name": item[data_schema["name"]],
//     "type": item[data_schema["type"]],
//     "industry": item[data_schema["industry"]],
//     "website": item[data_schema["website"]],
//     "logo": item[data_schema["logo"]],
//     "dividend_yield": item[data_schema["dividend_yield"]],
//     "years_dividend_growth": item[data_schema["years_dividend_growth"]], 
//     "growth_all_years_of_history": item[data_schema["growth_all_years_of_history"]], 
//     "payout_ratios": item[data_schema["payout_ratios"]],
//     "three_year_cagr": item[data_schema["three_year_cagr"]], 
//     "five_year_cagr": item[data_schema["five_year_cagr"]], 
//     "year_price_high": item[data_schema["year_price_high"]],
//     "year_price_low": item[data_schema["year_price_low"]],
//     "beta": item[data_schema["beta"]],
//     "backup_stock_price": item[data_schema["backup_stock_price"]],
//     "backup_stock_price_date_saved": item[data_schema["backup_stock_price_date_saved"]],
//     "dividend_payment_months_and_count": item[data_schema["dividend_payment_months_and_count"]],
//     "annual_dividend": item[data_schema["annual_dividend"]]
//     }
//     data_dict_array.append(data_dict)
//   return data_dict_array
















// @app.route("/dataquery", methods=["POST", "GET"])
// def get_portfolio_tickers() -> any:
//   tickers_submitted = request.get_json()
//   print(f"tickers submitted: {tickers_submitted}")
//   tickers_query = http_query_to_db_query_tickers(tickers_submitted)
//   query =  f"SELECT ticker, name, equity_type, industry, website, logo, dividend_yield, years_dividend_growth, growth_all_years_of_history, payout_ratios, three_year_cagr, five_year_cagr, year_price_high, year_price_low, beta, backup_stock_price, backup_stock_price_date_saved, dividend_payment_months_and_count, annual_dividends from grizzly_stocks WHERE {tickers_query}"
//   ticker_data = db_fetch(query)
//   data_dict = data_transform_to_dict(ticker_data)
//   return data_dict


function http_query_to_db_query_tickers(tickers) {
  console.log(tickers.length);
  if (tickers.length > 1) {
    let db_query = '';
    for (let i = 0; i < tickers.length; i++) {
      if (i === 0) {
        db_query += `ticker = '${tickers[i]}'`
      }
      else {
        db_query += ` OR ticker = '${tickers[i]}'`
      }
    }
    return db_query;
  }
  else {
    return `ticker = '${tickers[0]}'`;
  }
}


app.post('/dataquery', async (req, res) => {
  console.log('in data query');
  const tickers_submitted = req.body;
  console.log(tickers_submitted);
  const tickers_query = http_query_to_db_query_tickers(tickers_submitted)
  console.log(tickers_query);
  const sql = `SELECT ticker, name, equity_type, industry, website, logo, dividend_yield, years_dividend_growth, growth_all_years_of_history, payout_ratios, three_year_cagr, five_year_cagr, year_price_high, year_price_low, beta, backup_stock_price, backup_stock_price_date_saved, dividend_payment_months_and_count, annual_dividends from grizzly_stocks WHERE ${tickers_query}`;
  // const val =
  db.query(sql, (err, data) => {
    if (err) {
      return res.status(400).json({ error: 'Stock Retrieval Failed, try again'});
    } else {
      console.log(data);
      console.log(typeof(data))
      const json_data = JSON.stringify(data);
      console.log(typeof(json_data))
      // const success_msg = 'Stock data retrieval successful';
      return res.status(201).json({data: json_data});
    }
  })

  // try {
  //   console.log('in data query');
  //   const tickers_submitted = req.body;
  //   console.log(tickers_submitted);
  //   const tickers_query = http_query_to_db_query_tickers(tickers_submitted)
  //   // Assuming you have a table called 'your_table_name' with columns 'name' and 'value'
  //   console.log(tickers_query);
  //   const { rows } =await pool.query(`SELECT ticker, name, equity_type, industry, website, logo, dividend_yield, years_dividend_growth, growth_all_years_of_history, payout_ratios, three_year_cagr, five_year_cagr, year_price_high, year_price_low, beta, backup_stock_price, backup_stock_price_date_saved, dividend_payment_months_and_count, annual_dividends from grizzly_stocks WHERE ${tickers_query}`);

  //   // After successful insertion, fetch data from the database
  //   // const { rows } = await pool.query('SELECT * FROM your_table_name');
  //   console.log(rows);
  //   let json_rows = JSON.stringify(rows);
  //   res.status(201).json({ message: 'Data added successfully', data: json_rows });
  // } catch (error) {
  //   console.error('Error executing query:', error);
  //   res.status(500).json({ error: 'Internal Server Error' });
  // }
});


app.post('/login', async (req, res) => {
  const user_data = req.body;
  const submitted_username = user_data["username"];
  const submitted_password = user_data["password"];
  const login_query = `SELECT * from grizzly_users WHERE username = ? AND password = ?`;
  const login_params = [submitted_username, submitted_password];
  db.query(login_query, login_params, (err, data) => {
    if (err) {
      return res.status(400).json({ error: 'Login Failed, try again'});
    } else {
      console.log(data);
      const success_msg = 'User login successful';
      const failed_msg = 'Username or password incorrect';
      data.length === 1 ? res.status(201).json({ message: success_msg }) : res.status(400).json({ error: failed_msg});
    }
  })
});


// function insertNewUser(submitted_username, submitted_email, submitted_password) {

// }

app.post('/register', async (req, res) => {
  const user_data = req.body;
  const submitted_username = user_data["username"];
  const submitted_email = user_data["email"];
  const submitted_password = user_data["password"];
  const existing_query = `SELECT * from grizzly_users WHERE username = ? OR email = ?`;
  const existing_params = [submitted_username, submitted_email];
  db.query(existing_query, existing_params, (err, data) => {
    if (err) {
      return res.status(400).json({ error: 'Username or email is already taken' });
    }
    else {
      const insert_user_query = `INSERT INTO grizzly_users (username, email, password, join_date) VALUES (\'${submitted_username}\', \'${submitted_email}\', \'${submitted_password}\', \'${date}\')`;
      db.query(insert_user_query, (err, data2) => {
        if (data.length > 0) {
          return res.status(400).json({ error: 'Username or email is already taken' });
        }
        else {
          return res.status(201).json({ message: 'Registration added successfully' });
        }
    })
  }})
});



app.get('/searchtickers', async (req, res) => {
  const sql = 'SELECT ticker, name from grizzly_stocks WHERE industry IS NOT NULL AND dividend_yield IS NOT NULL AND years_dividend_growth IS NOT NULL AND payout_ratios IS NOT NULL AND three_year_cagr IS NOT NULL  AND five_year_cagr IS NOT NULL AND annual_dividends IS NOT NULL';
  db.query(sql, (err, data) => {
    if (err) return res.json("ERROR");
    return res.json(data);
  })


  // try {
    // Example query to test the connection
    // const { rows } = await pool.query('SELECT ticker, name from grizzly_stocks where has_dividend = \'true\' AND industry IS NOT NULL AND dividend_yield IS NOT NULL AND years_dividend_growth IS NOT NULL AND payout_ratios IS NOT NULL AND three_year_cagr IS NOT NULL  AND five_year_cagr IS NOT NULL AND annual_dividends IS NOT NULL');
    // console.log("RES JSONHIT");
    // console.log(rows);

  //   let str = JSON.stringify(rows);
  //   // console.log(str);
  //   res.send(str)
  // } catch (error) {
  //   console.error('Error executing query:', error);
  //   res.status(500).send('Error');
  // }
}
);




























app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});