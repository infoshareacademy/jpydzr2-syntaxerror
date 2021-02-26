import pandas as pd

class ProcessingData:
    def __init__(self):
        self.world_covid_data = False

    def refresh_world_data(self):
        world_covid_data = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', sep=',').to_csv('world_covid_data.csv',index=False, sep=',')
        return world_covid_data

    def show_world_covid_data(self):
        world_covid_data = pd.read_csv('world_covid_data.csv', sep=',')
        print(world_covid_data)

    def refresh_polish_data(self):
        polish_covid_data = pd.read_csv('https://www.arcgis.com/sharing/rest/content/items/153a138859bb4c418156642b5b74925b/data', sep=';', encoding='latin1').to_csv('polish_covid_data.csv',index=False, sep=';', encoding='utf-8')
        return polish_covid_data

    def show_polish_covid_data(self):
        polish_covid_data = pd.read_csv('polish_covid_data.csv', sep=';', encoding='utf-8')
        print(polish_covid_data)

