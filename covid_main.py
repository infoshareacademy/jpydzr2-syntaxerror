import covid_helper
from SQL_DB import *


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
            mycursor.execute("INSERT INTO logs (log) VALUES ('Pobrano dane')")
            mydb.commit()
            covid_helper.save_all_data()
        elif var == 2:
            date_start = input('Od RRRR-MM-DD\n')
            date_start_tmp = ('Wybrano date początkową ' + str(date_start))
            mycursor.execute("INSERT INTO logs (log) VALUES ('" + date_start_tmp + "')")
            mydb.commit()
            date_end = input('do RRRR-MM-DD\n')
            date_end_tmp = ('Wybrano date końcową ' +str(date_end))
            mycursor.execute("INSERT INTO logs (log) VALUES ('" + date_end_tmp + "')")
            mydb.commit()
        elif var == 3:
            covid_helper.read_all_data(date_start, date_end)
            scope_temp = ('Wybrano zakres ' + 'od: ' + str(date_start) + ' ' + 'do: ' + str(date_end) )
            mycursor.execute("INSERT INTO logs (log) VALUES ('" + scope_temp +"')")
            mydb.commit()
        elif var == 4:
            powiat = input('Podaj powiat\n')
            covid_helper.plot(powiat, date_start, date_end)
            plot_tmp = ('Wykres dla: ' + str(powiat) + 'w datach od: ' + str(date_start) + 'do: ' +str(date_end))
            mycursor.execute("INSERT INTO logs (log) VALUES ('" + plot_tmp + "')")
            mydb.commit()
        elif var == 5:
            covid_helper.plotcorrelation(date_start, date_end)
            corelation_tmp = ('Korelacja w okresie od: ' + str(date_start) + 'do: ' + str(date_end))
            mycursor.execute("INSERT INTO logs (log) VALUES ('" + corelation_tmp + "')")
            mydb.commit()
        elif var == 6:
            covid_helper.plot_map()
            mycursor.execute("INSERT INTO logs (log) VALUES ('Wykres mapy')")
            mydb.commit()
        elif var == 7:
            mycursor.execute("INSERT INTO logs (log) VALUES ('Exit')")
            mydb.commit()
            print(" Thank you for using the program! Bye!")
            exit()


if __name__ == '__main__':
    main()
