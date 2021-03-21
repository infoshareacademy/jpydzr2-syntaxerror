import pandas as pd
import datetime
import requests
import glob
import io
import os
import zipfile
from pathlib import Path

#SQL
import config
import mysql.connector
from sqlalchemy import create_engine


def fix_encoding(all_files, start_file_idx=None, end_file_idx=None,
                 encoding='utf-8'):

    """The function solves the issue of different csv encodings within
    the zip file. That could be read directly by 'pd.read_csv(ZIP FILE URL)'
    """

    for file in all_files[start_file_idx:end_file_idx]:
        file_name = Path(file).name

        # make a date minus 1 day (COVID results are from the previous day)
        d = datetime.date(int(file_name[:4]),  # day
                          int(file_name[4:6]),  # month
                          int(file_name[6:8])  # year
                          ) - datetime.timedelta(days=1)

        # read each file
        df = pd.read_csv(file, encoding=encoding, sep=';', header=0)

        # add or overwrite 'stan rekordu na'
        # as there are cases with missing data
        df['stan_rekordu_na'] = d

        # save as the same file name
        df.to_csv(file, header=True, encoding='utf-8', sep=';', index=False)


def save_covid_data(path):

    # link to the archived data per 'powiat'
    archiwalne = 'https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data'

    # folder where all the files will be  saved
    covid_path = path + '/' + 'covid_data'

    # create a subfolder for covid data
    if not os.path.exists(covid_path):
        os.makedirs(covid_path)

    # get and extract all csv from:
    # https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2
    r = requests.get(archiwalne).content
    z = zipfile.ZipFile(io.BytesIO(r))
    z.extractall(covid_path)

    # list of all csv with covid data
    all_files = sorted(glob.glob(covid_path + "/*.csv"))

    # iterate through all file names and extract dates
    # the first 30 files have utf-8 encoding
    fix_encoding(all_files, end_file_idx=30, encoding='utf-8')

    # from the 31st files, files have Windows-1250 encoding
    fix_encoding(all_files, start_file_idx=30, encoding='Windows-1250')


def read_covid_data(path):
    path = path
    all_files = sorted(glob.glob(path + "/*.csv"))

    # create a list of dataframes, [39:] selects only 2021 data
    list_of_dfs = [pd.read_csv(file, encoding='utf-8', sep=';', header=0) for
                   file in all_files[39:]]

    # concatenate all dataframes into one
    main_df = pd.concat(list_of_dfs, axis=0, ignore_index=True, sort=False)

    # remove 't' from teryt code and add 0 for teryt with 3 digits
    main_df['teryt'] = main_df['teryt'].str.replace('t', '')
    main_df['teryt'] = main_df['teryt'].apply(lambda x: '0' + str(x) if len(str(x)) < 4 else str(x))

    return main_df


def create_database(cursor, database):
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(database))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


if __name__ == '__main__':

    # read archived data
    save_covid_data('input')
    df = read_covid_data('input/covid_data')
    df['stan_rekordu_na'] = df['stan_rekordu_na'].astype('datetime64[s]')

    # create database
    cnx = mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.passwd)

    cursor = cnx.cursor()
    create_database(cursor, config.db_name)

    # create a table 'covid_19_powiat' from pandas df
    engine = create_engine('mysql+mysqlconnector://{user}:{passw}@{host}/{db}'
                           .format(user=config.user,
                                   passw=config.passwd,
                                   host=config.host,
                                   db=config.db_name))

    df.to_sql(name='covid_19_powiat', con=engine, if_exists='replace',
              index=False)