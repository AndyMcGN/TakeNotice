import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
from datetime import datetime, timedelta, date
from helpers import apology, mkdate, gbp, calc_interest, format_date
import calendar
from operator import itemgetter

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["gbp"] = gbp

db = SQL("sqlite:///rates.db")

@app.route("/", methods=["GET","POST"])
def index():
    db.execute("DROP TABLE IF EXISTS rel_dates")
    if request.method == "GET":
        product_list = db.execute("SELECT DISTINCT product_name, product_id FROM rates")
        return render_template("index.html", product_list=product_list)

    #  if submitting form, index checks the validity of inputs, then uses other functions to create
    #  a database (rel_dates) with the relevant info of the user's product

    # check that there is a valid amount
    try:
        amount = int(request.form.get("amount"))
    except ValueError:
        return apology("enter investment amount")
    if amount < 0:
        return apology("enter positive investment amount")

    # check there is an investment date
    try:
        invest_date = datetime.strptime(request.form.get("start"), "%Y-%m-%d").date()
    except:
        return apology("enter investment date")

    # get relevant product info
    product_id = request.form.get("product_id")
    product = db.execute("SELECT notice_length, change_date FROM rates WHERE product_id=:product_id ORDER BY change_date LIMIT 1", product_id=product_id)
    notice_period = timedelta(days=int(product[0]['notice_length']))
    start_date = datetime.strptime(product[0]['change_date'], "%Y-%m-%d").date()
    today = datetime.today().date()

    # if product's start date is after investment date throw error
    if invest_date < start_date:
        return apology("enter date after product started")

    # find status of product (withdrawn, active or notice given)
    # work out when withdrawal was/will be based on when notice given
    if request.form.get("matured_or_not") == "True":
        status = 'withdrawn'
        try:
            withdrawal = datetime.strptime(request.form.get("withdrawal"), "%Y-%m-%d").date()
        except:
            return apology("enter withdrawal date or select different option")
    elif request.form.get("notice_or_not") == "True":
        status = 'unfinished_notice'
        try:
            notice_given = datetime.strptime(request.form.get("notice_date"), "%Y-%m-%d").date()
            withdrawal = notice_given + notice_period
        except:
            return apology("enter notice date or select different option")
        if notice_given < invest_date:
            return apology("enter notice date after investment date")
    else:  # notice not given, work out how much they would get if thez gave notice today
        status= 'active'
        withdrawal = today + notice_period
    # check that withdrawal date is valid
    if withdrawal <= invest_date:
        return apology("investment date must be before withdrawal date")


    # create database to store changes, end of months and interest earned etc.basically all info relevant to this persons product
    rel_changes = create_table(invest_date, withdrawal, product_id)

    # add ends of months into relevant dates
    end_of_month = datetime(invest_date.year, invest_date.month, calendar.monthrange(invest_date.year, invest_date.month)[1]).date()
    rel_dates = add_dates(end_of_month, withdrawal, status, product_id)

    rel_dates = make_readable_dates(rel_dates)  # turn string dates into readable datetimes

    complete_first_line(rel_dates, invest_date, withdrawal, amount, status)  # add info on first row of table (algorithm needs to be different for first line)

    complete_table(rel_dates, withdrawal, amount)  # add info to rest of database

    return summary()

@app.route("/summary")
def summary():

    today = datetime.today().date()
    earnings= db.execute("SELECT * FROM rel_dates WHERE end_date <= :today ORDER BY start_date", today=today)
    future_earnings = db.execute("SELECT * FROM rel_dates WHERE start_date >= :today ORDER BY start_date", today=today)
    status = earnings[0]['status']
    print(f"status in summary= {status}")
    return render_template("results.html", earnings=earnings, future_earnings=future_earnings, status=status)

@app.route("/breakdown")
def breakdown():
    today = datetime.today().date()
    earnings= db.execute("SELECT * FROM rel_dates WHERE end_date <= :today ORDER BY start_date", today=today)
    print(earnings)
    future_earnings = db.execute("SELECT * FROM rel_dates WHERE start_date >= :today ORDER BY start_date", today=today)
    return render_template("breakdown.html", earnings=earnings, future_earnings=future_earnings)

@app.route("/add", methods=["GET","POST"])
def add():
    # if on page because of link
    if request.method == "GET":
        return render_template("add.html")

    # if submitting form
    # get info from add form
    form = request.form
    product_name = request.form.get("product_name")
    start_rate = request.form.get("start_rate")
    start_date = request.form.get("start_date")

    # check initial fields are filled in
    if not product_name:
        return apology("please name product")
    if not start_date:
        return apology("please add start date")
    if not start_rate:
        return apology("please enter rate")

    # check if name is taken
    dup_check = db.execute("SELECT * FROM rates WHERE product_name= :product", product=product_name)
    if len(dup_check) != 0:
        return apology("product name taken")
    # see how many products we already have saved to give this product the next id
    old_ids = db.execute("SELECT count(DISTINCT product_name) as 'count' FROM 'rates'")
    new_id = old_ids[0]['count'] + 1

    notice_length = request.form.get("notice_length")

    # insert values into database
    db.execute("INSERT INTO rates (product_name, rate, change_date, product_id, notice_length) VALUES (:product, :start_rate, :start_date, :id, :notice_length)", product=product_name, start_rate=start_rate, start_date=start_date, id=new_id, notice_length=notice_length)

    # go through form inserting any changes into database
    n = 1
    for i in range(int(((len(form)-3)/2))):
        change_date = form[f'date_{n}']
        new_rate = form[f'rate_{n}']

        # TODO check all fields have been filled in (would be better if i could do this before i start adding to db)
        if not change_date:
            db.execute("DELETE FROM rates WHERE product_id = :id", id= new_id)
            return apology("make sure fields are filled in")

        db.execute("INSERT INTO rates (product_name, rate, change_date, product_id, notice_length) VALUES (:product, :new_rate, :change_date, :id, :notice_length)", product=product_name, new_rate=new_rate, change_date=change_date, id=new_id, notice_length=notice_length)
        n+=1
        print(new_rate)
        print(change_date)
    product_list = db.execute("SELECT DISTINCT product_name, product_id FROM rates")

    return render_template("index.html", product_list=product_list)

# add_months function adapted form David Webb and Scott Staffored's answer on Stackoverflowhttps://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
def add_months(sourcedate, months):
    month = sourcedate.month  - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = calendar.monthrange(year,month)[1]
    return date(year, month, day)

def create_table(invest_date, withdrawal, product_id):
    db.execute("CREATE TABLE rel_dates (id integer PRIMARY KEY, start_date datetime, end_date datetime, period integer, rate numeric, interest numeric(5,2), cum_interest numeric(5,2), cum_funds numeric(5,2), is_change boolean, status varchar(17))")
    db.execute("INSERT INTO rel_dates (start_date, rate, is_change) SELECT change_date, rate, is_change FROM rates WHERE change_date BETWEEN :invest_date AND :end_date AND product_id= :product_id OR rate_id IN (SELECT rate_id FROM rates WHERE change_date < :invest_date AND product_id = :product_id ORDER BY change_date DESC LIMIT 1)", invest_date=invest_date, end_date=withdrawal, product_id=product_id)
    rel_changes = db.execute("SELECT * FROM rel_dates")
    return rel_changes

def add_dates(end_of_month, withdrawal, status, product_id):
    rel_changes = db.execute("SELECT * FROM rel_dates")
    change = 0

    while end_of_month < withdrawal:
        # if try creates error, it is the last row of rel_changes, in which case just add a final line to rel_dates using current rates
        try:
            change_date = mkdate(rel_changes[change + 1]['start_date'])
        except:
            rate = rel_changes[change]['rate']
            db.execute("INSERT INTO rel_dates (start_date, rate, is_change) VALUES (:last_day, :rate, 'False')", last_day=end_of_month, rate=rate)
            break

        if end_of_month > change_date:  # if last day of month comes after a rate change, move onto next rate
            change = change + 1

        rate = rel_changes[change]['rate']
        db.execute("INSERT INTO rel_dates (start_date, rate, is_change) VALUES (:change_date, :rate, 'False')", change_date=end_of_month, rate=rate)
        end_of_month = add_months(end_of_month, 1)
        # if it comes before the next rate change, enter it into rel_dates with old rate
        # else enter it into the rel_dates with new rate and move cursor onto next one

    # add today into the table if product not already withdrawn
    if status != "withdrawn":
        today = datetime.today().date()
        current_rate = db.execute("SELECT * FROM rates WHERE change_date < :today AND product_id = :product_id ORDER BY change_date DESC LIMIT 1", product_id=product_id, today=today)
        current_rate = current_rate[0]['rate']
        print(f"CURRENT RATE IS {current_rate}")
        db.execute("INSERT INTO rel_dates (start_date, rate, is_change) VALUES (:today, :current_rate, 'False')", today=today, current_rate=current_rate)

    rel_dates = db.execute("SELECT * FROM rel_dates ORDER BY start_date")
    return rel_dates

def make_readable_dates(rel_dates):
    for date in range(len(rel_dates)):
        new_date = mkdate(str(rel_dates[date]['start_date']))
        rel_dates[date]['start_date'] = new_date
    return rel_dates

def complete_first_line(rel_dates, invest_date, withdrawal, amount, status):
    if len(rel_dates) == 1:  # if no rate changes or end of month between deposit and withdrawal  1
        period = withdrawal - invest_date + timedelta(days=1)
        start = invest_date
        end = withdrawal

    else:  # first change in table  2
        print("First line")
        change = rel_dates[1]['start_date']
        period = change - invest_date + timedelta(days=1)
        start = invest_date
        end = change

    interest = calc_interest(period, amount, rel_dates,1, end)
    amount = amount + interest
    db.execute("UPDATE rel_dates SET start_date = :invest_date, end_date = :end, period = :period, interest = :interest, cum_interest= :interest, cum_funds=:cum_funds, status=:status WHERE start_date= :start", invest_date=invest_date, end=end, period=period.days, interest=interest, start=rel_dates[0]['start_date'], cum_funds=amount, status=status)

def complete_table(rel_dates, withdrawal, amount):
    n = 2
    for rate in range(len(rel_dates)-1):
        if n == len(rel_dates):  # last row  3
            print("case 3")
            print(f"n = {n}")
            last_change = mkdate(str(rel_dates[n-1]['start_date']))
            period = withdrawal - last_change
            start = last_change
            end = withdrawal
            print(n)

        else:  #  middle rows in rel_dates  4
            print("case 4")
            print(f"n = {n}")
            change = mkdate(str(rel_dates[n]['start_date']))
            last_change = mkdate(str(rel_dates[n-1]['start_date']))
            period = change - last_change
            start = last_change
            end = change

        interest = calc_interest(period, amount, rel_dates,n, end)
        amount = amount + interest
        cum_interest = db.execute("SELECT SUM(interest) FROM rel_dates")
        cum_interest = cum_interest[0]['SUM(interest)'] + interest
        print(f"cum_interest= {cum_interest}")
        print(f"'start_date': {start}, 'end_date': {end}, 'period': {period.days}, 'rate': {rel_dates[n-1]['rate']}, 'interest': {gbp(interest)}, 'cum_funds': {gbp(amount)}")
        db.execute("UPDATE rel_dates SET end_date = :end, period = :period, interest = :interest, cum_interest=:cum_interest, cum_funds=:cum_funds  WHERE start_date= :start", start=str(start), end=end, period=period.days, interest=interest, cum_interest=cum_interest, cum_funds=amount)
        n += 1