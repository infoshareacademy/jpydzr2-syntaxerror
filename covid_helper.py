import pandas as pd
import geopandas as gpd
import requests, glob, zipfile, io, os
import datetime
from pathlib import Path

# visualization
import matplotlib.pyplot as plt
import seaborn as sns

base_color = sns.color_palette()[0]


class RequestData:
    def __init__(self, id: int, description: str, year: int, filename: str) -> None:
        self.id = id
        self.description = description
        self.year = year
        self.filename = filename


def _get_total_records(url):
    request = requests.get(url)
    data = request.json()
    return data['totalRecords']


def _get_gus_data_from_all_pages(url: str):
    total_records = _get_total_records(url)

    max_records_per_page = 100
    pages = int(total_records / max_records_per_page)
    GUS_data = {}

    for page in range(0, pages + 1):
        url_pages = url + f'&page={page}&page-size=100'
        req = requests.get(url_pages, headers={'X-ClientId': '38dfdca8-de37-41fc-44ab-08d8830c4874'})
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
        RequestData(64428, 'przecietne wynagrodzenie brutto', 2019, 'Wynagrodzenie')
    ]

    unit_level = 5  # poziom agregacji 5 - powiaty

    for gus_variable in gus_variables:
        url = f'https://bdl.stat.gov.pl/api/v1/data/by-variable/{gus_variable.id}?unit-level={unit_level}&year={gus_variable.year}'

        GUS_data = _get_gus_data_from_all_pages(url)

        df_GUS_data = pd.DataFrame(data=GUS_data, index=['Location', gus_variable.description]).transpose()
        df_GUS_data.to_csv(gus_output_path + '/' + gus_variable.filename)


def fix_encoding(all_files, start_file_idx=None, end_file_idx=None, encoding='utf-8'):
    for file in all_files[start_file_idx:end_file_idx]:
        file_name = Path(file).name

        # make a date and subtract 1 day (COVID results are from the previous day)
        # breakpoint()
        d = datetime.date(int(file_name[:4]), int(file_name[4:6]), int(file_name[6:8])) - datetime.timedelta(days=1)

        # read each file
        df = pd.read_csv(file, encoding=encoding, sep=';', header=0)

        # add 'stan rekordu na' if does not exist or overwrite the existing date
        df['stan_rekordu_na'] = d

        # save as the same file name
        df.to_csv(file, header=True, encoding='utf-8', sep=';', index=False)


def save_covid_data(path):
    # link to the archived data per 'powiat'
    # the last day of the archived data is equal to the latest CSV from the actual data
    archiwalne = 'https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data'

    # link to the geo locations of powiat
    mapa_powiatow = 'https://www.gis-support.pl/downloads/Powiaty.zip'

    # folder where all the files will be  saved
    path = path
    geo_path = path + '/' + 'geo_data'
    covid_path = path + '/' + 'covid_data'

    # create a subfolder for geo data
    if not os.path.exists(geo_path):
        os.makedirs(geo_path)

    # get and extract all geo data
    r = requests.get(mapa_powiatow).content
    z = zipfile.ZipFile(io.BytesIO(r))
    z.extractall(geo_path)

    # create a subfolder for covid data
    if not os.path.exists(covid_path):
        os.makedirs(covid_path)

    # get and extract all csv from https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2
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
    list_of_dfs = [pd.read_csv(file, encoding='utf-8', sep=';', header=0) for file in all_files[39:]]

    # concatenate all dataframes into one
    main_df = pd.concat(list_of_dfs, axis=0, ignore_index=True, sort=False)

    # remove 't' from teryt code and add 0 for teryt with 3 digits
    main_df['teryt'] = main_df['teryt'].str.replace('t', '')
    main_df['teryt'] = main_df['teryt'].apply(lambda x: '0' + str(x) if len(str(x)) < 4 else str(x))

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


def plot_map(df, path):
    # read goe data
    map_df = gpd.read_file(path + '/Powiaty.shp')

    # show only the latest results
    last_result = df.stan_rekordu_na.max()
    df_last_results = df[df.stan_rekordu_na == last_result][['teryt', 'liczba_przypadkow', 'stan_rekordu_na']]

    # join datasets
    dane_mapa = pd.merge(map_df, df_last_results, how='left', left_on='JPT_KOD_JE', right_on='teryt')
    dane_mapa = dane_mapa.to_crs(epsg=2180)

    # plot the map
    fig, ax = plt.subplots(1, figsize=(10, 10))
    plt.title(f'Liczba przypadkow na {last_result}', fontsize=16, fontweight='bold')
    dane_mapa.plot(column='liczba_przypadkow', ax=ax, cmap='YlOrRd', linewidth=0.8, edgecolor='gray')
    ax.axis('off')
    plt.show()

def merge_data():
    df_COVID = read_covid_data(args.read_path + '/' + 'covid_data')
    df_GUS = pd.read_csv(args.read_path + '/' + 'gus_data' + '/' + 'Wynagrodzenie')

    df_GUS['Location'] = df_GUS['Location'].apply(lambda x: x.lower().split()[-1])
    df_GUS['Location'] = df_GUS['Location'].apply(lambda x: x.split('.')[-1])

    df_COVID['powiat_miasto'] = df_COVID['powiat_miasto'].apply(lambda x: x.lower())
    #print(df_COVID.info())
    df_COVID['liczba_na_10_tys_mieszkancow'] = df_COVID['liczba_na_10_tys_mieszkancow'].apply(lambda x: float(str(x).replace(',','.')))
    #print(df_COVID.info())
    df_grouped = df_COVID.groupby('powiat_miasto')['liczba_na_10_tys_mieszkancow'].mean()

    df_GUS = df_GUS.drop(df_GUS.columns[0], axis=1)
    df_merged = df_GUS.merge(df_grouped, left_on='Location', right_on='powiat_miasto', how='inner')

    plt.title(f'Korelacja')
    sns.scatterplot(data=df_merged, x='liczba_na_10_tys_mieszkancow', y='przecietne wynagrodzenie brutto')
    #plt.plot(df_merged['liczba_przypadkow'], df_merged['przecietne wynagrodzenie brutto'], line_style= '-.')
    # df_merged['liczba_przypadkow'].plot(figsize=(16, 8))
    # df_merged['przecietne wynagrodzenie brutto'].plot(figsize=(16, 8))
    plt.legend()
    #plt.show()

    corr = np.corrcoef(df_merged['przecietne wynagrodzenie brutto'], df_merged['liczba_na_10_tys_mieszkancow'])
    print(corr)

    #print(df_merged)

    # for index, row in df_COVID.iterrows():
    #     for index2, row2 in df_GUS.iterrows():
    #         data = str(row['powiat_miasto']).lower()
    #         data2 = str(row2['Location']).lower()
    #         if data==data2:
    #             print(data)

    #print(df_COVID)