import pandas as pd
import geopandas as gpd
import requests, glob, zipfile, io, os
import datetime

# visualization
import matplotlib.pyplot as plt
import seaborn as sns

base_color = sns.color_palette()[0]

def save_GUS_data(path):
    gus_path = path + '/' + 'gus_data'

    # create a subfolder for geo data
    if not os.path.exists(gus_path):
        os.makedirs(gus_path)

    # Chosen Variables:
    # 72305 - liczba mieszkancow
    # 746289 - mediana wieku ludnosci
    # 1601437 - liczba boisk futbolowych - tylko 2018
    # 1241 - liczba muzeow
    # 64428 - przecietne wynagrodzenie brutto

    variables = {
        72305: ['liczba mieszkancow', 2019, 'Mieszkancy'],
        746289: ['mediana wieku ludnosci',2019, 'Mediana'],
        1601437: ['liczba boisk futbolowych', 2018, 'Boiska'],
        1241: ['liczba muzeow', 2019, 'Muzea'],
        64428: ['przecietne wynagrodzenie brutto', 2019, 'Wynagrodzenie']
    }

    unit_level = 5  # poziom agregacji 5 - powiaty

    for key, item in variables.items():

        url = f'https://bdl.stat.gov.pl/api/v1/data/by-variable/{key}?unit-level={unit_level}&year={item[1]}'
        req = requests.get(url)
        data = req.json()

        total_records = data['totalRecords']
        pages = int(total_records / 100)

        GUS_data = {}

        for page in range(0, pages + 1):
            url_pages = url + f'&page={page}&page-size=100'
            req = requests.get(url_pages, headers={'X-ClientId': '38dfdca8-de37-41fc-44ab-08d8830c4874'})
            data = req.json()

            for elem in data['results']:
                GUS_data[elem['id']] = [elem['name'], elem['values'][0]['val']]
                #print("{}: {} - {}".format(elem['id'], elem['name'], elem['values'][0]['val']))
        df_GUS_data = pd.DataFrame(data=GUS_data, index=['Location', item[0]]).transpose()
        df_GUS_data.to_csv(gus_path + '/' + item[2])

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
    for file in all_files[:30]:
        file_name = file.replace(covid_path + '/', '')

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
        file_name = file.replace(covid_path + '/', '')

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

# TODO: download GUS data
# TODO: calculate the average cases per inhabitants