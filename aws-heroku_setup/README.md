# Analyse COVID-19 situation in Poland
### Team: # jpydzr2-syntaxerror
<span style="color: gray; font-size:1em;">Project start: Mar-2021</span>

## Problem
 [Past COVID-19 data](https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data) is provided as a .zip file, containing all .csv from previous months. There is a problem with .csv encodings, that prevents pandas to read these .csv on the fly with `pd.read_csv(ZIP URL)`. This forces an user to download and unzip all the files on a local drive each time he wants to interact with the app.

## AWS RDS: COVID-19 data
 - The AWS RDS solves the problem of downloading and processing the data on a local drive.
 - How to start with AWS RDS: [Creating a MySQL DB instance and connecting to a database on a MySQL DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.MySQL.html)
 -  `aws-rds_setup.py` contains all functions used for data preprocessing and loading to AWS RDS with pandas.


## Heroku: COVID-19 data daily update

 - How to start with Heroku: [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python)
 -  `heroku_setup.py` contains all functions used for data preprocessing and loading to AWS RDS with pandas. The script was deployed on heroku and scheduled to run every day at 8pm UTC with Heroku Scheduler add-on.
 -  The script loads/appends only the [current COVID-19 data](https://www.arcgis.com/sharing/rest/content/items/6ff45d6b5b224632a672e764e04e8394/data)
