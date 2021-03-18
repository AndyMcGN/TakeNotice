CS50x Final Project - TakeNotice
Andrew McGinn

This web application calculates the current and future interest rates of notice accounts.
Interest on notice accounts is tricky to calculate as the rates often change and the interest is compounded monthly.
This app takes user input on the amount and dates invested and calculates how long the investment earnt each rate of
interest before it changed.

At the bank where I work, customer services do not currently have any way of working out the interest on customers' accounts and
when they phone up asking about it, we have to tell them that they can only find out by giving their notice and waiting until they
can access their funds - less than ideal, so this will be really helpful for us!

Products are kept with info on their rates and dates in a MySQL database, and a temporary database is created for a user's
investment, which stores the amount earnt at each rate. This info is presented as a summary and as a table of interest gained each
month of the investment.

For this project, I used HTML, CSS, Bootstrap and JavaScript for the frontend and Python with a flask framework for the backend,
along with the MySQL databases and Jinja within the HTML.