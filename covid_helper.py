import pandas as pd
import requests, glob, zipfile, io
import datetime


def download_covid_data(path):
    # link to the archived data per 'powiat'
    # the last day of the archived data is equal to the latest CSV from the actual data
    archiwalne = 'https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data'

    # folder where all the files will be  saved
    path = path
    all_files = glob.glob(path + "/*.csv")

    # get and extract all csv from https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2
    r = requests.get(archiwalne).content
    z = zipfile.ZipFile(io.BytesIO(r))
    z.extractall(path)

    # iterate through all file names and extract dates
    for file in all_files:
        file_name = file.replace(path + '/', '')

        # make a date and subtract 1 day (COVID results are from the previous day)
        d = datetime.date(int(file_name[:4]), int(file_name[4:6]), int(file_name[6:8])) - datetime.timedelta(days=1)

        # read each file
        df = pd.read_csv(file, encoding='latin1', sep=';', header=0)

        # add 'stan rekordu na' if does not exist or overwrite the existing date
        df['stan_rekordu_na'] = d

        # save as the same file name
        df.to_csv(file, header=True, sep=';', index=False)


def load_and_read_csv(path):
    path = path
    all_files = sorted(glob.glob(path + "/*.csv"))

    # create a list of dataframes, [39:] selects only 2021 data
    list_of_dfs = [pd.read_csv(file, encoding='latin1', sep=';', header=0) for file in all_files[39:]]

    # concatenate all dataframes into one
    main_df = pd.concat(list_of_dfs, axis=0, ignore_index=True, sort=False)

    return main_df
