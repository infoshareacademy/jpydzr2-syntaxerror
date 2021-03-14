import covid_helper

def main():
    print("Witaj w COVID APP")
    date_start = None
    date_end = None

    while True:
        print("1 - Pobierz dane\n"
              "2 - Ustaw zakres dat\n"
              "3 - Wczytaj i wyswietl dane\n"
              "4 - Wykres\n"
              "5 - Mapa\n"
              "6 - Update danych\n"
              "7 - Koniec")

        var = int(input())
        if var == 1:
            covid_helper.save_all_data()
        elif var == 2:
            date_start = input('Od RRRR-MM-DD\n')
            date_end = input('do RRRR-MM-DD\n')
        elif var == 3:
            covid_helper.read_all_data(date_start, date_end)
        elif var == 4:
            powiat = input('Podaj powiat\n')
            covid_helper.plot(powiat, date_start, date_end)
        elif var == 5:
            covid_helper.plotmap()
        elif var == 6:
            covid_helper.update()
        elif var == 7:
            exit()

if __name__ == '__main__':
    main()
