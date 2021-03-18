import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime


def mkdate(mysql_date):
    date = datetime.strptime(mysql_date, "%Y-%m-%d").date()
    return date

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def gbp(value):
    """Format value as GBP."""
    return f"£{value:,.2f}"

def daysInYear(year):
    if year % 400 == 0:
        return 366
    elif year % 100 == 0:
        return 365
    elif year % 4 == 0:
        return 366
    else:
        return 365
#  Algorithm from Wikipedia entry on Leap Years (https://en.wikipedia.org/wiki/Leap_year)


def calc_interest (period, amount, rate_table, n, end):
    year = end.year
    year_days = daysInYear(year)
    interest = period.days * ((amount*(rate_table[n-1]['rate']/100)/year_days))  # 366 if year is leap year like 2020 find/make function giving no of days in year as input
    print(f"{period} days, {amount}* {rate_table[n-1]['rate']}/100/{year_days}")
    return interest

def format_date(date):
    """Format as british date"""
    return date.strftime("%d/%m/%Y")
