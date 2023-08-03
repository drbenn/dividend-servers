thing = {'symbol': 'APA', 'historical': [{'date': '2023-07-20', 'label': 'July 20, 23', 'adjDividend': 0.25, 'dividend': 0.25, 'recordDate': '2023-07-21', 'paymentDate': '2023-08-22', 'declarationDate': '2023-05-22'}, {'date': '2023-04-20', 'label': 'April 20, 23', 'adjDividend': 0.25, 'dividend': 0.25, 'recordDate': '2023-04-21', 'paymentDate': '2023-05-22', 'declarationDate': '2023-02-02'}, {'date': '2023-01-20', 'label': 'January 20, 23', 'adjDividend': 0.25, 'dividend': 0.25, 'recordDate': '2023-01-23', 'paymentDate': '2023-02-22', 'declarationDate': '2022-12-13'}, {'date': '2022-10-20', 'label': 'October 20, 22', 'adjDividend': 0.25, 'dividend': 0.25, 'recordDate': '2022-10-21', 'paymentDate': '2022-11-22', 'declarationDate': '2022-09-14'}, {'date': '2022-07-21', 'label': 'July 21, 22', 'adjDividend': 0.125, 'dividend': 0.125, 'recordDate': '2022-07-22', 'paymentDate': '2022-08-22', 'declarationDate': '2022-05-12'}, {'date': '2022-04-21', 'label': 'April 21, 22', 'adjDividend': 0.125, 'dividend': 0.125, 'recordDate': '2022-04-22', 'paymentDate': '2022-05-23', 'declarationDate': '2022-02-04'}, {'date': '2022-01-20', 'label': 'January 20, 22', 'adjDividend': 0.125, 'dividend': 0.125, 'recordDate': '2022-01-21', 'paymentDate': '2022-02-22', 'declarationDate': '2021-11-03'}, {'date': '2021-10-21', 'label': 'October 21, 21', 'adjDividend': 0.063, 'dividend': 0.063, 'recordDate': '2021-10-22', 'paymentDate': '2021-11-22', 'declarationDate': '2021-09-20'}, {'date': '2021-07-21', 'label': 'July 21, 21', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2021-07-22', 'paymentDate': '2021-08-23', 'declarationDate': '2021-05-27'}, {'date': '2021-04-21', 'label': 'April 21, 21', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2021-04-22', 'paymentDate': '2021-05-21', 'declarationDate': '2021-02-05'}, {'date': '2021-01-21', 'label': 'January 21, 21', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2021-01-22', 'paymentDate': '2021-02-22', 'declarationDate': '2020-12-07'}, {'date': '2020-10-21', 'label': 'October 21, 20', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2020-10-22', 'paymentDate': '2020-11-23', 'declarationDate': '2020-09-16'}, {'date': '2020-07-21', 'label': 'July 21, 20', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2020-07-22', 'paymentDate': '2020-08-21', 'declarationDate': '2020-05-14'}, {'date': '2020-04-21', 'label': 'April 21, 20', 'adjDividend': 0.025, 'dividend': 0.025, 'recordDate': '2020-04-22', 'paymentDate': '2020-05-22', 'declarationDate': '2020-02-07'}]}


# print(len(thing["historical"]))

# newThing = {'symbol': thing["symbol"], 'historical': thing["historical"][5]}
# print(newThing)


# junk = "https://www.something.com/sadfasdfasdf"

# val = -1
# for i in range(0, 3):
#     val = junk("/", val + 1)

# print(val)

# Initialising values
ini_str = "https://www.something.com/sadfasdfasdf"
sub_str = "/"
occurrence = 3
 
# Finding nth occurrence of substring
val = -1
for i in range(0, occurrence):
  val = ini_str.find(sub_str, val + 1)
   
# Printing nth occurrence
print ("Nth occurrence is at", val)

new_site = ini_str[:val + 1]

print(new_site)