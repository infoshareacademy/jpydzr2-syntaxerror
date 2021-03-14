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
    print("Data have been saved.")


def read(powiat, date_start, date_end):
    df = covid_helper.read_covid_data(arg_parser().read_path + '/' + 'covid_data')
    print("Data have been loaded. Below is the snippet.")
    start = df[df['stan_rekordu_na'] == date_start].index[0]
    end = df[df['stan_rekordu_na'] == date_end].index[-1]
    filter_ = df['powiat_miasto'].str.contains(powiat)
    print(df[filter_].loc[start:end])



def plot(powiat, date_start, date_end):
    df = covid_helper.read_covid_data(arg_parser().read_path + '/' + 'covid_data')
    covid_helper.plot_chart(df, powiat, date_start, date_end)

'''    if args.save:
        covid_helper.save_covid_data(args.save_path)
        covid_helper.save_GUS_data(args.save_path)
        covid_helper.save_gis_data(args.save_path)
        print("Data have been saved.")

    elif args.update:
        covid_helper.update_covid_data(args.update_path)
        print("COVID data have been updated.")

    elif args.read:
        df_COVID = covid_helper.read_covid_data(args.read_path + '/' + 'covid_data')
        df_GUS = covid_helper.read_GUS_Data(args.read_path + '/' + 'gus_data')
        print("Data have been loaded. Below is the snippet.")
        print(df_COVID.head())
        print(df_GUS.head())

        df_COVID = covid_helper.filter_group_COVID(df_COVID)

        df_merged = covid_helper.merge_data(df_COVID, df_GUS)

        print(df_merged.head())'''


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
          "5 - Koniec")
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


if __name__ == '__main__':
    main()
