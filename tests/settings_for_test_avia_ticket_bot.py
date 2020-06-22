import datetime
import calendar

import avia_settings
import all_flights
import avia_handlers

TOWN_DEPARTURE = 'Москва'
TOWN_ARRIVAL = 'Лондон'
QUANTITY_PLACES = '2'
COMMENT_FOR_BOOKING = 'комментарий'
NUMBER_OF_DATE = 5
TELEPHONE = '8-(888)-888-88 88'

INPUTS = [
    'Привет',
    '/help',
    '/ticket',
    'Город',
    TOWN_DEPARTURE,
    'Караганда',
    '/ticket',
    TOWN_DEPARTURE,
    'лондона',
    '12.12.2020',
    '25-05-2020',
    '7',
    str(NUMBER_OF_DATE),
    '7',
    QUANTITY_PLACES,
    COMMENT_FOR_BOOKING,
    'не знаю',
    'нет',
    TOWN_DEPARTURE,
    'Лондон',
    '25-05-2020',
    str(NUMBER_OF_DATE),
    QUANTITY_PLACES,
    COMMENT_FOR_BOOKING,
    'да',
    TELEPHONE,
    '/ticket',
    '/help',
    'не знаю',
    'да',
    '/stop'
]

possible_towns = ''
for town_arrival in all_flights.ALL_POSSIBLE_FLIGHTS[TOWN_DEPARTURE]:
    possible_towns += f'{town_arrival}, '

possible_flights = [datetime.datetime(year=2020, month=5, day=25, hour=5, minute=5),
                    datetime.datetime(year=2020, month=5, day=25, hour=5, minute=25),
                    datetime.datetime(year=2020, month=5, day=25, hour=15, minute=15),
                    datetime.datetime(year=2020, month=5, day=25, hour=15, minute=35),
                    datetime.datetime(year=2020, month=5, day=25, hour=15, minute=45)]
possible_flights_list = ''
for i, flight in enumerate(possible_flights):
    possible_flights_list += (f'{i + 1}. {calendar.day_name[flight.weekday()]}, '
                              f'{flight.strftime(avia_handlers.FORMAT_OUT_DATE)}\n')

date = (f'{calendar.day_name[possible_flights[NUMBER_OF_DATE - 1].weekday()]}, '
        f'{possible_flights[NUMBER_OF_DATE - 1].strftime(avia_handlers.FORMAT_OUT_DATE)}')

EXPECTED_OUTPUTS = [
    avia_settings.DEFAULT_ANSWER,
    avia_settings.INTENTS[0]['answer'],
    avia_settings.SCENARIOS['booking']['steps']['step1']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step1']['failure_text'].format(
        towns_departures=all_flights.towns_departures,
        towns_arrival=all_flights.towns_arrival),
    avia_settings.SCENARIOS['booking']['steps']['step2']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        possible_towns=possible_towns),
    avia_settings.SCENARIOS['booking']['steps']['step2']['failure_text'].format(town_departure=TOWN_DEPARTURE,
                                                                                town_arrival='караганда'),
    avia_settings.SCENARIOS['booking']['steps']['step1']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step2']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        possible_towns=possible_towns),
    avia_settings.SCENARIOS['booking']['steps']['step3']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step3']['failure_text'],
    avia_settings.SCENARIOS['booking']['steps']['step4']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        town_arrival=TOWN_ARRIVAL,
                                                                        possible_flights_list=possible_flights_list),
    avia_settings.SCENARIOS['booking']['steps']['step4']['failure_text'].format(town_departure=TOWN_DEPARTURE,
                                                                                town_arrival=TOWN_ARRIVAL,
                                                                                possible_flights_list=possible_flights_list),
    avia_settings.SCENARIOS['booking']['steps']['step5']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step5']['failure_text'],
    avia_settings.SCENARIOS['booking']['steps']['step6']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step7']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        town_arrival=TOWN_ARRIVAL,
                                                                        date=date,
                                                                        quantity_places=QUANTITY_PLACES,
                                                                        comment_for_booking=COMMENT_FOR_BOOKING),
    avia_settings.SCENARIOS['booking']['steps']['step7']['failure_text'],
    f"Заказ билета запущен заново!\n{avia_settings.SCENARIOS['booking']['steps']['step1']['text']}",
    avia_settings.SCENARIOS['booking']['steps']['step2']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        possible_towns=possible_towns),
    avia_settings.SCENARIOS['booking']['steps']['step3']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step4']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        town_arrival=TOWN_ARRIVAL,
                                                                        possible_flights_list=possible_flights_list),
    avia_settings.SCENARIOS['booking']['steps']['step5']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step6']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step7']['text'].format(town_departure=TOWN_DEPARTURE,
                                                                        town_arrival=TOWN_ARRIVAL,
                                                                        date=date,
                                                                        quantity_places=QUANTITY_PLACES,
                                                                        comment_for_booking=COMMENT_FOR_BOOKING),
    avia_settings.SCENARIOS['booking']['steps']['step8']['text'],
    avia_settings.SCENARIOS['booking']['steps']['step9']['text'].format(telephone=TELEPHONE),
    avia_settings.SCENARIOS['booking']['steps']['step1']['text'],
    avia_settings.INTENTS[0]['answer'] + avia_settings.SCENARIOS_PAUSE['wish_to_continue'],
    avia_settings.SCENARIOS_PAUSE['continue_or_not'],
    avia_settings.SCENARIOS['booking']['steps']['step1']['text'],
    avia_settings.STOP_SCENARIO['answer']
]
