# Finance

Note: This project previously used Yahoo finance to get the data. But since last few months Yahoo has discontinued it's service.
The project now uses Alphavantage. But unlike Yahoo it does not return company's name. So the stock symbol itself is used as a placeholder for company's name.

Personalized Version of CS50's PSET. (<https://docs.cs50.net/2018/x/psets/7/finance/finance.html>)

A web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks' actual prices and portfolios' values, it will also let you buy (okay, "buy") and sell (okay, "sell") stocks by querying alphavantage for updated stocks' prices.

# How to run

1. Install **pip3** (package manager for Python).
2. Enter **pip3 install -r requirements.txt** in terminal.
3. Enter **export FLASK_APP=application.py** in terminal. 
4. Enter **flask run** 
5. Open browser with url mentioned in the above command.
6. Profit.

- Create Virtual environment if needed before installing the packages(<https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments>).

# What You can do in this

1. Create Account.
2. Quote Stocks.
3. Buy Stocks.
4. Sell Stocks. (You might make profit or loss depending on the value of the stock at that time)
5. View latest news.
6. Subscribe to the companies of your intrest and get their news in perticular.
7. Create wishlist.

# Screenshots


![sample shot](/screenshots/finance1.png?raw=true)
<br>
![sample shot](/screenshots/finance2.png?raw=true)
<br>
![sample shot](/screenshots/finance3.png?raw=true)
