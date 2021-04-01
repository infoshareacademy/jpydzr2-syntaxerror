import covid_helper
import SQL_DB


def data_download():
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('Pobrano dane')")
    SQL_DB.mydb.commit()
    covid_helper.save_all_data()


def date_range_start():
    date_start = input('Od RRRR-MM-DD\n')
    date_start_tmp = ('Wybrano date początkową ' + str(date_start))
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('" + date_start_tmp + "')")
    SQL_DB.mydb.commit()
    return date_start


def date_range_end():
    date_end = input('do RRRR-MM-DD\n')
    date_end_tmp = ('Wybrano date końcową ' + str(date_end))
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('" + date_end_tmp + "')")
    SQL_DB.mydb.commit()
    return date_end


def data_show(date_start, date_end):
    covid_helper.read_all_data(date_start, date_end)
    scope_temp = ('Wybrano zakres ' + 'od: ' + str(date_start) + ' ' + 'do: ' + str(date_end))
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('" + scope_temp + "')")
    SQL_DB.mydb.commit()


def plot_show(date_start, date_end):
    powiat = input('Podaj powiat\n')
    covid_helper.plot(powiat, date_start, date_end)
    plot_tmp = ('Wykres dla: ' + str(powiat) + 'w datach od: ' + str(date_start) + 'do: ' + str(date_end))
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('" + plot_tmp + "')")
    SQL_DB.mydb.commit()


def corelation_plot_show(date_start, date_end):
    covid_helper.plotcorrelation(date_start, date_end)
    corelation_tmp = ('Korelacja w okresie od: ' + str(date_start) + 'do: ' + str(date_end))
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('" + corelation_tmp + "')")
    SQL_DB.mydb.commit()


def map_show():
    covid_helper.plot_map()
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('Wykres mapy')")
    SQL_DB.mydb.commit()


def app_exit():
    SQL_DB.mycursor.execute("INSERT INTO logs (log) VALUES ('Exit')")
    SQL_DB.mydb.commit()
    print(" Thank you for using the program! Bye!")
    exit()


def main():
    print("Witaj w COVID APP")
    date_start = None
    date_end = None

    while True:
        print("1 - Pobierz dane GUS\n"
              "2 - Ustaw zakres dat\n"
              "3 - Wczytaj i wyswietl dane\n"
              "4 - Wykres\n"
              "5 - Wykres Korelacji\n"
              "6 - Mapa\n"
              "7 - Koniec")

        var = int(input())
        if var == 1:
            data_download()
        elif var == 2:
            date_start = date_range_start()
            date_end = date_range_end()
        elif var == 3:
            data_show(date_start, date_end)
        elif var == 4:
            plot_show(date_start, date_end)
        elif var == 5:
            corelation_plot_show(date_start, date_end)
        elif var == 6:
            map_show()
        elif var == 7:
            app_exit()


if __name__ == '__main__':
    main()
