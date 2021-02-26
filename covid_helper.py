import pandas as pd
import requests, glob, zipfile, io
import datetime

# visualization
import matplotlib.pyplot as plt
# %matplotlib inline

import seaborn as sns

base_color = sns.color_palette()[0]


def save_covid_data(path):
    # link to the archived data per 'powiat'
    # the last day of the archived data is equal to the latest CSV from the actual data
    archiwalne = 'https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data'

    # folder where all the files will be  saved
    path = path
    all_files = sorted(glob.glob(path + "/*.csv"))

    # get and extract all csv from https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2
    r = requests.get(archiwalne).content
    z = zipfile.ZipFile(io.BytesIO(r))
    z.extractall(path)

    # iterate through all file names and extract dates
    # the first 30 files have utf-8 encoding
    for file in all_files[:30]:
        file_name = file.replace(path + '/', '')

        # make a date and subtract 1 day (COVID results are from the previous day)
        d = datetime.date(int(file_name[:4]), int(file_name[4:6]), int(file_name[6:8])) - datetime.timedelta(days=1)

        # read each file
        df = pd.read_csv(file, encoding='utf-8', sep=';', header=0)

        # add 'stan rekordu na' if does not exist or overwrite the existing date
        df['stan_rekordu_na'] = d

        # save as the same file name
        df.to_csv(file, header=True, encoding='utf-8', sep=';', index=False)

    # from the 31st files, files have Windows-1250 encoding
    for file in all_files[30:]:
        file_name = file.replace(path + '/', '')

        # make a date and subtract 1 day (COVID results are from the previous day)
        d = datetime.date(int(file_name[:4]), int(file_name[4:6]), int(file_name[6:8])) - datetime.timedelta(days=1)

        # read each file
        df = pd.read_csv(file, encoding='Windows-1250', sep=';', header=0)

        # add 'stan rekordu na' if does not exist or overwrite the existing date
        df['stan_rekordu_na'] = d

        # save as the same file name
        df.to_csv(file, header=True, encoding='utf-8', sep=';', index=False)


def read_covid_data(path):
    path = path
    all_files = sorted(glob.glob(path + "/*.csv"))

    # create a list of dataframes, [39:] selects only 2021 data
    list_of_dfs = [pd.read_csv(file, encoding='utf-8', sep=';', header=0) for file in all_files[39:]]

    # concatenate all dataframes into one
    main_df = pd.concat(list_of_dfs, axis=0, ignore_index=True, sort=False)

    return main_df


def plot_chart(df, powiat):
    df_copy = df[df['powiat_miasto'] == powiat].copy()
    df_copy.index = df_copy['stan_rekordu_na']
    df_copy['liczba_przypadkow_7d_MA'] = df_copy['liczba_przypadkow'].rolling(7).mean()

    plt.title(f'Liczba przypadkow dla {powiat}')
    df_copy['liczba_przypadkow'].plot(figsize=(16, 8))
    df_copy['liczba_przypadkow_7d_MA'].plot(figsize=(16, 8))
    plt.legend()
    plt.show()
