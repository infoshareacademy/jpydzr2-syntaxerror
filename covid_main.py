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


def main():
    # Get input arguments
    args = arg_parser()

    if args.save:
        covid_helper.save_covid_data(args.save_path)
        covid_helper.save_GUS_data(args.save_path)
        covid_helper.save_gis_data(args.save_path)
        print("Data have been saved.")

    elif args.update:
        covid_helper.update_covid_data(args.update_path)
        print("COVID data have been updated.")

    elif args.read:
        df = covid_helper.read_covid_data(args.read_path + '/' + 'covid_data')
        print("Data have been loaded. Below is the snippet.")
        print(df.head())

    elif args.plot:
        df = covid_helper.read_covid_data(args.read_path + '/' + 'covid_data')
        covid_helper.plot_chart(df, args.powiat)

    elif args.plot_map:
        df = covid_helper.read_covid_data(args.read_path + '/' + 'covid_data')
        covid_helper.plot_map(df, args.read_path + '/' + 'geo_data')

    else:
        print('No arguments provided. Please check -h for help.')


if __name__ == '__main__':
    main()
