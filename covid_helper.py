import os
import config
from sqlalchemy import create_engine
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

base_color = sns.color_palette()[0]


class RequestData:
    def __init__(self, id: int, description: str, year: int,
                 filename: str) -> None:
        self.id = id
        self.description = description
        self.year = year
        self.filename = filename


def _data_path():
    path = os.getcwd() + '/input'
    return path


def save_all_data():
    save_GUS_data(_data_path())
    print("Data have been saved.")


def read_all_data(date_start, date_end):
    df_COVID = read_covid_data()
    df_GUS = read_GUS_Data(_data_path() + '/' + 'gus_data')

    df_COVID = filter_group_COVID(df_COVID, date_start, date_end)
    df_merged = merge_data(df_COVID, df_GUS)

    print("Data have been loaded. Below is the snippet.")

    print(df_merged.head())


def plot(powiat, date_start, date_end):
    df = read_covid_data()
    plot_chart(df, powiat, date_start, date_end)


def _get_total_records(url):

    for _ in range(1,5):
        try:
            request = requests.get(url)
            assert(request.status_code == requests.codes.ok)
            break
        except Exception as e:
            print(f'Error occurred: {e.__class__}. Trying again.')

    data = request.json()
    return data['totalRecords']


def _get_gus_data_from_all_pages(url: str):
    total_records = _get_total_records(url)

    max_records_per_page = 100
    pages = int(total_records / max_records_per_page)
    GUS_data = {}

    for page in range(0, pages + 1):
        url_pages = url + f'&page={page}&page-size=100'

        for _ in range(1, 5):
            try:
                req = requests.get(url_pages, headers={
                    'X-ClientId': '38dfdca8-de37-41fc-44ab-08d8830c4874'})
                assert (req.status_code == requests.codes.ok)
                break
            except Exception as e:
                print(f'Error occurred: {e.__class__}. Trying again.')

        data = req.json()

        for elem in data['results']:
            GUS_data[elem['id']] = [elem['name'], elem['values'][0]['val']]

    return GUS_data


def save_GUS_data(path):
    gus_output_path = path + '/' + 'gus_data'

    if not os.path.exists(gus_output_path):
        os.makedirs(gus_output_path)

    gus_variables = [
        RequestData(72305, 'liczba mieszkancow', 2019, 'Mieszkancy'),
        RequestData(746289, 'mediana wieku ludnosci', 2019, 'Mediana'),
        RequestData(1601437, 'liczba boisk futbolowych', 2018, 'Boiska'),
        RequestData(1241, 'liczba muzeow', 2019, 'Muzea'),
        RequestData(64428, 'przecietne wynagrodzenie brutto', 2019,'Wynagrodzenie'),
        RequestData(1508, 'zanieczyszczenie powietrza', 2019, 'Zanieczyszczenie'),
    ]

    unit_level = 5  # poziom agregacji 5 - powiaty

    for gus_variable in gus_variables:
        url = f'https://bdl.stat.gov.pl/api/v1/data/by-variable/{gus_variable.id}?unit-level={unit_level}&year={gus_variable.year}'

        GUS_data = _get_gus_data_from_all_pages(url)

        df_GUS_data = pd.DataFrame(data=GUS_data,
                                   index=['Location', gus_variable.description]
                                   ).transpose()
        df_GUS_data.to_csv(gus_output_path + '/' + gus_variable.filename)


def read_covid_data():

    engine = create_engine('mysql+mysqlconnector://{user}:{passw}@{host}/{db}'
                           .format(user=config.user,
                                   passw=config.passwd,
                                   host=config.host,
                                   db=config.db_name))

    df = pd.read_sql('SELECT * FROM covid_19_powiat', con=engine)

    df['teryt'] = df['teryt'].str.replace('t', '')
    df['teryt'] = df['teryt'].apply(
        lambda x: '0' + str(x) if len(str(x)) < 4 else str(x))

    return df


def plot_chart(df, powiat, date_start, date_end):
    df_copy = df[df['powiat_miasto'] == powiat].copy()  # Przekazanie powiatu

    if date_start is not None and date_end is not None:
        df_copy = df_copy.loc[(df_copy['stan_rekordu_na'] <= date_end) & (
                    df_copy['stan_rekordu_na'] >= date_start)]

    df_copy.index = df_copy['stan_rekordu_na']

    for no, col in enumerate(df_copy.columns):
        print(no, col)

    x = int(input("Which data should I plot?: "))

    df_copy['7d_Moving_Average'] = (df_copy[df_copy.columns[x]]
                                          .rolling(7)
                                          .mean()
                                          )

    plt.title(f'{df_copy.columns[x]} dla {powiat}')
    df_copy[df_copy.columns[x]].plot(figsize=(16, 8))
    df_copy['7d_Moving_Average'].plot(figsize=(16, 8))
    plt.legend()
    plt.show()


def plot_map():
    # read geo data
    mapa_powiatow = 'https://www.gis-support.pl/downloads/Powiaty.zip'
    map_df = gpd.GeoDataFrame.from_file(mapa_powiatow)

    # read covid data
    engine = create_engine('mysql+mysqlconnector://{user}:{passw}@{host}/{db}'
                           .format(user=config.user,
                                   passw=config.passwd,
                                   host=config.host,
                                   db=config.db_name))

    covid_df = pd.read_sql('SELECT teryt, liczba_przypadkow, stan_rekordu_na FROM covid_19_powiat', con=engine)

    covid_df['teryt'] = covid_df['teryt'].str.replace('t', '')
    covid_df['teryt'] = covid_df['teryt'].apply(
        lambda x: '0' + str(x) if len(str(x)) < 4 else str(x))

    # show only the latest results
    last_result = covid_df.stan_rekordu_na.max()
    df_last_results = covid_df[covid_df.stan_rekordu_na == last_result][
        ['teryt', 'liczba_przypadkow', 'stan_rekordu_na']]

    # join datasets
    dane_mapa = pd.merge(map_df, df_last_results, how='left',
                         left_on='JPT_KOD_JE', right_on='teryt')
    dane_mapa = dane_mapa.to_crs(epsg=2180)

    # plot the map
    fig, ax = plt.subplots(1, figsize=(10, 10))
    plt.title(f'Liczba przypadkow na {last_result}', fontsize=16,
              fontweight='bold')
    dane_mapa.plot(column='liczba_przypadkow', ax=ax, cmap='YlOrRd',
                   linewidth=0.8, edgecolor='gray')
    ax.axis('off')
    plt.show()


def read_GUS_Data(path=os.getcwd() + '/input/gus_data'):
    GUS_path = path

    df_GUS = None

    for filename in os.listdir(GUS_path):
        if df_GUS is None:
            df_GUS = pd.read_csv(GUS_path + '/' + filename)
            df_GUS.drop(df_GUS.columns[2], axis=1, inplace=True)

        df_GUS_temp = pd.read_csv(GUS_path + '/' + filename)
        df_GUS[filename] = df_GUS_temp[df_GUS_temp.columns[2]]

    return df_GUS


def filter_group_COVID(df_COVID, date_from=None, date_to=None):
    df_COVID['liczba_na_10_tys_mieszkancow'] = df_COVID[
        'liczba_na_10_tys_mieszkancow'].apply(
        lambda x: float(str(x).replace(',', '.')))
    df_COVID['powiat_miasto'] = df_COVID['powiat_miasto'].apply(
        lambda x: x.lower())

    if date_from is not None and date_to is not None:
        df_COVID = df_COVID.loc[(df_COVID['stan_rekordu_na'] <= date_to) & (
                    df_COVID['stan_rekordu_na'] >= date_from)]

    # df.loc[(df['column_name'] >= A) & (df['column_name'] <= B)]
    # df_copy = df[df['powiat_miasto'] == powiat].copy()  # Przekazanie powiatu

    df_grouped = df_COVID.groupby('powiat_miasto').mean()

    return df_grouped


def merge_data(df_COVID, df_GUS):
    df_GUS['Location'] = df_GUS['Location'].apply(
        lambda x: x.lower().split()[-1])
    df_GUS['Location'] = df_GUS['Location'].apply(lambda x: x.split('.')[-1])

    df_GUS = df_GUS.drop(df_GUS.columns[0], axis=1)
    df_merged = df_GUS.merge(df_COVID, left_on='Location',
                             right_on='powiat_miasto', how='inner')



    return df_merged


def plotcorrelation(date_from: None, date_to: None):
    df_GUS = read_GUS_Data()
    df_COVID = read_covid_data()

    df_COVID = filter_group_COVID(df_COVID, date_from, date_to)
    df_merged = merge_data(df_COVID, df_GUS)

    for no, col in enumerate(df_merged.columns):
        print(no, col)

    x = int(input("Provide X Axis: "))
    y = int(input("Provide Y Axis: "))

    plt.title(f'Korelacja')

    sns.scatterplot(data=df_merged, x=str(df_merged.columns[x]), y=str(df_merged.columns[y]))

    plt.show()

    corr = np.corrcoef(df_merged[df_merged.columns[x]], df_merged[df_merged.columns[y]])
    print(f'Correlation coefficient {corr}')