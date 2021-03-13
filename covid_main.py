import argparse
import covid_helper


def arg_parser():
    """In a console:
    "python3 covid_main.py" = saves data in the default location 'input' and reads df

    "python3 covid_main.py --save" = saves data in the default location 'input'
    "python3 covid_main.py --save -d 'your path'" = saves data in the user specified location

    "python3 covid_main.py --read" = once saved, reads df
    "python3 covid_main.py --read -r 'your path'" = once saved, reads df from the user specified location

    "python3 covid_main.py --plot" = plots daily cases with 7days moving average, default for 'Cały kraj'
    "python3 covid_main.py --plot -p 'powiat'" = plots daily cases with 7days moving average for specified powiat
    """

    # define parser
    parser = argparse.ArgumentParser(description="COVID Data")

    # prevents running multiple arguments at the same time
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--save', action='store_true', help='Downloads COVID and geo data')
    group.add_argument('--read', action='store_true', help='Shows first 5 results of COVID dataset')
    group.add_argument('--plot', action='store_true', help='Plots a line chart per powiat')
    group.add_argument('--plot_map', action='store_true', help='Plots a map for the last known date')

    # optional argument
    parser.add_argument('-s', '--save_path', default='input',
                        help='Provide a location to save all data. Default = input')
    parser.add_argument('-r', '--read_path', default='input',
                        help='Provide a location to read COVID data. Default = input')
    parser.add_argument('-p', '--powiat', default='Cały kraj',
                        help='Provide powiat you want to analyze. Default = Cały kraj')

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
