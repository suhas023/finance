from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import string
import feedparser

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
flag = 0
@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT symbol,shares FROM portfolio WHERE id=:id",id=session["user_id"])

    new_price = 0
    total_price = 0

    for row in rows:
        sub_price = 0
        shares = row["shares"]
        symbol = row["symbol"]
        new_symbol = lookup(symbol)
        new_price = new_symbol["price"]
        sub_price = shares*new_price
        total_price += sub_price

        db.execute("UPDATE portfolio SET total=:tot,price=:pri WHERE id=:id AND symbol=:symbol",tot=sub_price,pri=new_price,
        id=session["user_id"],symbol=symbol)




    row2 = db.execute("SELECT cash FROM users WHERE id=:id",id=session["user_id"])
    cash = row2[0]["cash"]
    total = cash + total_price;


    portfolio = db.execute("SELECT * FROM portfolio WHERE id=:id ORDER BY symbol",id=session["user_id"])

    return render_template("index.html",portfolio = portfolio,cash=usd(cash),total = usd(total))








@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""

    if request.method == "POST":




        if not request.form.get("Symbol"):
            return apology("Missing Symbol")
        else:
            Symbol = lookup(str(request.form.get("Symbol")))


        if not Symbol:
            return apology("Invalid Symbol")

        if not request.form.get("Shares"):
            return apology("Enter Shares")

        else:
            try:
                No = int(request.form.get("Shares"))
            except ValueError:
                return apology("Invalid characters")

        if No < 0:
            return apology("Shares less than zero")


        #get Budget from user
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        cash = (cash[0].get("cash"))

        #Check if he can afford
        if No*Symbol.get("price") > cash:
            return apology("Insufficient Funds")

        #Insert purchase to History
        db.execute("INSERT INTO history  (id,sym,shares,price) VALUES (:id,:sym,:shares,:price)",id=session["user_id"]
        ,sym=Symbol.get("symbol"),shares=No,price=(Symbol.get("price")))

        #check if Symbol was already purchased
        rows = db.execute("SELECT * FROM portfolio WHERE id=:id AND symbol=:sym",id=session["user_id"],sym=Symbol.get("symbol"))

        if not rows:
            #Add row of Symbol if not already purchased
            db.execute("INSERT INTO portfolio VALUES(:id,:symbol,:name,:shares,:price,:total)",id=session["user_id"],
            symbol=Symbol.get("symbol"),name=Symbol.get("name"),shares=No,price=(Symbol.get("price")),total=str((No*Symbol.get("price"))))

        else:
            #only update the No. of stocks if already had purchased
            db.execute("UPDATE portfolio SET shares=:shares+:No WHERE id=:id AND symbol=:sym",shares=rows[0]["shares"],No=No,
            id=session["user_id"],sym=Symbol.get("symbol"))

        #Update the remaining Budget
        db.execute("UPDATE users SET cash=:value WHERE id=:id",value=cash-No*Symbol.get("price"),id=session["user_id"])


    else:
        return render_template("buy.html")






    flash("Bought!")
    return redirect(url_for("index"))

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""

    rows = db.execute("SELECT * FROM history WHERE id=:id  ORDER BY Transacted",id=session["user_id"])


    return render_template("history.html",rows = rows)


    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")


        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in

        session["user_id"] = rows[0]["id"]
        
        # if user is redirected to login send to the request page
        if not request.args.get("next") == "None" and request.args.get("next") :
            return redirect(request.args.get("next"))
        
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        

        return render_template("login.html",nextX = request.args.get("next"))

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        result = lookup(str(request.form.get("quote2")))
        if not result:
            return apology("Invalid Symbol")

        return render_template("valid_quote.html",name = result["name"],share = result["price"],symbol = result["symbol"])
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Must Provide Username")


        #Check if user already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if  rows:
            return apology("User Already exists")

        elif not request.form.get("password") or not request.form.get("conform_password"):
            return apology("Password/Conformation Password  Missing!")

        elif request.form.get("password") != request.form.get("conform_password"):
            return apology("Password Dont Match")


        else:
            db.execute("INSERT INTO users (username,hash) VALUES (:username,:hash)",username = request.form.get("username"),
            hash = pwd_context.hash(request.form.get("password")))
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]

            return redirect(url_for("index"))


    else :
        return render_template("register.html")







@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("Enter Symbol")

        if not request.form.get("shares") :
            return apology("Enter shares")

        No = request.form.get("shares")
        symbol = request.form.get("symbol")


        try:
            if int(No) < 0:
                return apology("Shares cant be negative")

        except  ValueError:
            return apology("Invalid Type")



        if not lookup(symbol):
            return apology("Invalid Symbol")

        result = lookup(symbol)
        price = result["price"]
        No = int(No)


        rows = db.execute("SELECT shares FROM portfolio WHERE id=:id AND symbol=:symbol",id=session["user_id"],symbol=result["symbol"])

        if not (rows) or (No > rows[0]["shares"]) :
            return apology(str(rows))

        money = round(float(No*price),2)

        db.execute("UPDATE users SET cash=cash+:money WHERE id=:id",money=money,id=session["user_id"])

        if rows[0]["shares"] == No:
            db.execute("DELETE FROM portfolio WHERE id=:id AND symbol=:symbol",id=session["user_id"],symbol=result["symbol"])

        else :
            db.execute("UPDATE portfolio SET shares=shares - :No WHERE id=:id AND symbol=:symbol",No=No,id=session["user_id"],symbol=result["symbol"])

        db.execute("INSERT INTO history  (id,sym,shares,price) VALUES (:id,:sym,:shares,:price)",id=session["user_id"]
        ,sym=symbol,shares=-No,price=price)

        flash("Sold!")

        return redirect(url_for("index"))

    else:
        return render_template("sell.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password of user"""

    if request.method == "POST":
        old_pass=request.form.get("old_pass")
        new_pass=request.form.get("new_pass")
        new_pass2=request.form.get("new_pass2")


        row = db.execute("SELECT hash FROM users WHERE id=:id",id=session["user_id"])

        if not pwd_context.verify(old_pass, row[0]["hash"]):
            return apology("Invalid","old PassWord")

        if new_pass != new_pass2:
            return apology("Passwords Dont Match")

        db.execute("UPDATE users SET hash=:hash WHERE id=:id",hash=pwd_context.hash(new_pass),id=session["user_id"])

        flash("Password Successfully Updated!!")
        return redirect(url_for("index"))

    else:
        return render_template("change_password.html")




@app.route("/news",methods=["GET","POST"])
@login_required
def news():
    """Display the general news"""

    feed = feedparser.parse("https://news.google.com/news/rss/headlines/section/topic/BUSINESS.en_in/")
    return render_template("news.html",feed = feed["entries"])




@app.route("/my_news",methods=["GET","POST"])
@login_required
def my_news():
    """Display the the news custamized for the user"""
    url = "http://finance.yahoo.com/rss/headline?s={}"
    
    if request.method == "POST":
        symbols = request.form.get("symbols")
        symbols = symbols.split(",")

        

        look_up = []
        feed = {}

        for sym in symbols:
            if lookup(sym):
                look_up.append(sym)

        if len(look_up) == 0:
            return render_template("apology.html",top="Invalid Symbol")

        for sym in look_up:
            feed[sym] = feedparser.parse(url.format(sym))["entries"]

            if not db.execute("SELECT * FROM news WHERE id=:id AND symbol=:sym",id = session["user_id"],sym = sym):
                db.execute("INSERT INTO news VALUES(:id,:symbol)",id = session["user_id"],symbol = sym)

        return render_template("my_news.html",feed = feed,filled = True)


    else:

        rows =  db.execute("SELECT * FROM news WHERE id=:id",id = session["user_id"])

        if not rows:
            return render_template("my_news.html",filled = False)

        feed = {}
        
        for row in rows:
            feed[row["symbol"]] = feedparser.parse(url.format(row["symbol"]))["entries"]

        return render_template("my_news.html",feed = feed,filled = True)



@app.route("/wishlist",methods=["GET","POST"])
@login_required
def wishlist():
    """Display/Store symbols user is interested"""

    if request.method == "POST":

        symbols =  request.form.get("symbols")
        symbols = symbols.split(",")
        look_up = []

        for sym in symbols:
            if lookup(sym):
                look_up.append(sym)

        if len(look_up) == 0:
            return render_template("apology.html",top="Invalid Symbol")

        for sym in look_up:
            if not db.execute("SELECT * FROM wishlist WHERE id=:id AND symbol=:sym",id = session["user_id"],sym = sym):
                db.execute("INSERT INTO wishlist VALUES(:id,:symbol)",id = session["user_id"],symbol = sym)

        flash("Added to wishlist")

        return redirect(url_for("wishlist"))

    else:
        rows = db.execute("SELECT * FROM wishlist WHERE id=:id ORDER by symbol ",id = session["user_id"])

        if len(rows) == 0:
            return render_template("wishlist.html",filled = False)

        symbols = []

        for row in rows:
            symbols.append(lookup(row["symbol"]))

        return render_template("wishlist.html",filled = True, rows = symbols)








        


















