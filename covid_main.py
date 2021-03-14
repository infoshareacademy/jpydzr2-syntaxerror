import argparse
import covid_helper


def arg_parser():
    """In a console:

    "python3 covid_main.py -h" = to display the options
    """

    # define parser
    parser = argparse.ArgumentParser(description="COVID Data")

    # prevents running multiple arguments at the same time
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--save', action='store_true',
                       help='Downloads COVID, GIS and GUS data')
    group.add_argument('--update', action='store_true',
                       help='Update COVID data')
    group.add_argument('--read', action='store_true',
                       help='Shows first 5 results of COVID dataset')
    group.add_argument('--plot', action='store_true',
                       help='Plots a line chart per powiat')
    group.add_argument('--plot_map', action='store_true',
                       help='Plots a map for the last known date')

    # optional argument
    parser.add_argument('-s', '--save_path', default='input',
                        help='Provide a location to save all data. '
                             'Default = input')
    parser.add_argument('-u', '--update_path', default='input',
                        help='Provide a location for updated COVID data. '
                             'Default = input')
    parser.add_argument('-r', '--read_path', default='input',
                        help='Provide a location to read COVID data. '
                             'Default = input')
    parser.add_argument('-p', '--powiat', default='Cały kraj',
                        help='Provide powiat you want to analyze. '
                             'Default = Cały kraj')

    # Parse args
    args = parser.parse_args()
    return args


def save():
    covid_helper.save_covid_data(arg_parser().save_path)
    covid_helper.save_GUS_data(arg_parser().save_path)
    covid_helper.save_gis_data(arg_parser().save_path)

    print("Data have been saved.")


def read(powiat, date_start, date_end):
    df_COVID = covid_helper.read_covid_data(arg_parser().read_path + '/' + 'covid_data')
    print("Data have been loaded. Below is the snippet.")

    start = df_COVID[df_COVID['stan_rekordu_na'] == date_start].index[0]
    end = df_COVID[df_COVID['stan_rekordu_na'] == date_end].index[-1]
    filter_ = df_COVID['powiat_miasto'].str.contains(powiat)
    print(df_COVID[filter_].loc[start:end])

    df_GUS = covid_helper.read_GUS_Data(arg_parser().read_path + '/' + 'gus_data')
    df_COVID = covid_helper.filter_group_COVID(df_COVID)

    df_merged = covid_helper.merge_data(df_COVID, df_GUS)

    print(df_merged.head())

def update():
        covid_helper.update_covid_data(arg_parser().update_path)
        print("COVID data have been updated.")

def plot(powiat, date_start, date_end):
    df = covid_helper.read_covid_data(arg_parser().read_path + '/' + 'covid_data')
    covid_helper.plot_chart(df, powiat, date_start, date_end)

def plotmap():
    df = covid_helper.read_covid_data(arg_parser().read_path + '/' + 'covid_data')
    covid_helper.plot_map(df, arg_parser().read_path + '/' + 'geo_data')


def main():
    print("Witaj w COVID APP")
    powiat = input('Podaj powiat\n')
    date_start = input('Od RRRR-MM-DD\n')
    date_end = input('do RRRR-MM-DD\n')
    print("1 - Pobierz dane\n"
          "2 - Wczytaj dane\n"
          "3 - Wykres\n"
          "4 - Mapa\n"
          "5 - Koniec\n"
          "6 - Update")
    while True:
        var = int(input())
        if var == 1:
            save()
        elif var == 2:
            read(powiat, date_start, date_end)
        elif var == 3:
            plot(powiat, date_start, date_end)
        elif var == 4:
            plotmap()
        elif var == 5:
            exit()
        elif var == 6:
            update()

if __name__ == '__main__':
    main()
