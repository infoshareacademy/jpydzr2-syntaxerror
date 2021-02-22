import pandas as pd

dfTemporaryCovid = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', sep=',').to_csv('daneCovid.csv', sep=',')
covidData = pd.read_csv('daneCovid.csv', sep=',')