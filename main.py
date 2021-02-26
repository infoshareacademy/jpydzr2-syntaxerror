from sources import *
import logging


logging.basicConfig(filename='activity.log', level=logging.INFO)

ProcessingData().refresh_world_data()
logging.info('# ProcessingData().refresh_world_data()')

ProcessingData().show_world_covid_data()
logging.info('ProcessingData().show_world_covid_data()')

ProcessingData().refresh_polish_data()
logging.info('ProcessingData().refresh_polish_data()')

ProcessingData().show_polish_covid_data()
logging.info('ProcessingData().show_polish_covid_data()')
