import datetime
from cs50 import SQL
from helpers import mkdate
from operator import itemgetter
import calendar
from datetime import datetime, timedelta, date



db = SQL("sqlite:///rates.db")

# list of dicts with relevant rate changes (from one before investment to the end)
rel_dates = db.execute("SELECT change_date, rate, is_change FROM rates WHERE change_date BETWEEN '2020-09-03' AND '2021-12-20' AND product_id= 1 OR rate_id IN (SELECT rate_id FROM rates WHERE change_date < '2020-09-03' AND product_id = 1 ORDER BY change_date DESC LIMIT 1)")


rel_dates = sorted(rel_dates, key=itemgetter('change_date'))

invest_date = date(2020, 9, 3)
first_month = datetime.strptime(rel_dates[0]['change_date'], "%Y-%m-%d").date()
withdrawal = date(2020,12, 20)
first_rate = rel_dates[0]['rate']

last_day_of_month = date(invest_date.year, invest_date.month, calendar.monthrange(invest_date.year, invest_date.month)[1])

# add_months function adapted form David Webb and Scott Staffored's answer on Stackoverflowhttps://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
def add_months(sourcedate, months):
    month = sourcedate.month  - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = calendar.monthrange(year,month)[1]
    return date(year, month, day)

change = 0
change_date = mkdate(rel_dates[change + 1]['change_date'])
print(f"Last day of first month = {last_day_of_month}")


print("changes:")
print("________________________________________________")

while last_day_of_month < withdrawal:
    if last_day_of_month < change_date:  # if last day of month comes before a rate change
        rate = rel_dates[change]['rate']
        rel_dates.append({'change_date': last_day_of_month, 'rate': rate, 'is_change': False})

    else:
        change = change + 1
        rate = rel_dates[change]['rate']
        rel_dates.append({'change_date': last_day_of_month, 'rate': rate, 'is_change': False})

    last_day_of_month = add_months(last_day_of_month, 1)
    print(last_day_of_month)


    # if it comes before the next rate change, enter it into rel_dates with old rate
    # else enter it into the rel_dates with new rate and move cursor onto next one

for date in range(len(rel_dates)):
    new_date = mkdate(str(rel_dates[date]['change_date']))
    rel_dates[date]['change_date'] = new_date

rel_dates = sorted(rel_dates, key=itemgetter('change_date'))
print('relevant dates:')
for date in rel_dates:
    print(date)


# calculate interest earned


