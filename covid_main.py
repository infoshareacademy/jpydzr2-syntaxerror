import argparse
import covid_helper
import pandas


def arg_parser():
    """In a console:
    "python3 covid_main.py" = saves data in the default location 'COVID_archive' and reads df

    "python3 covid_main.py --save" = saves data in the default location 'COVID_archive'
    "python3 covid_main.py --save -d 'your path'" = saves data in the user specified location

    "python3 covid_main.py --read" = once saved, reads df
    "python3 covid_main.py --read -r 'your path'" = once saved, reads df from the user specified location
    """

    # define parser
    parser = argparse.ArgumentParser(description="COVID Data Download Settings")

    # prevents running --save and --read at the same time if typed manually
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--save', action='store_true')
    group.add_argument('--read', action='store_true')

    # optional argument
    parser.add_argument('-s', '--save_path', default='COVID_archive',
                        help='Download location for COVID data. Default = COVID_archive')
    parser.add_argument('-r', '--read_path', default='COVID_archive',
                        help='Location of the folder with COVID data. Default = COVID_archive')

    # Parse args
    args = parser.parse_args()
    return args


def main():
    # Get input arguments
    args = arg_parser()

    if args.save:
        covid_helper.save_covid_data(args.save_path)
        print("Data have been saved.")

    elif args.read:
        df = covid_helper.read_covid_data(args.read_path)
        print("Data have been loaded. Below is the snippet.")
        print(df.head())

    else:
        covid_helper.save_covid_data(args.save_path)
        print("Data have been saved.")

        df = covid_helper.read_covid_data(args.read_path)
        print("Data have been loaded. Below is the snippet.")
        print(df.head())


if __name__ == '__main__':
    main()
