import pandas as pd

# SQL
import config
from sqlalchemy import create_engine


def main():

    engine = create_engine('mysql+mysqlconnector://{user}:{passw}@{host}/{db}'
                           .format(user=config.user,
                                   passw=config.passwd,
                                   host=config.host,
                                   db=config.db_name))
    aktualne = 'https://www.arcgis.com/sharing/rest/content/items/6ff45d6b5b224632a672e764e04e8394/data'

    # read csv
    df = pd.read_csv(aktualne, encoding='Windows-1250', sep=';', header=0)

    # change the datatype to datetime (for timedelta)
    df['stan_rekordu_na'] = df['stan_rekordu_na'].astype('datetime64[s]')

    df.to_sql(name='covid_19_powiat', con=engine, if_exists='append',
              index=False)


if __name__ == '__main__':
    main()
