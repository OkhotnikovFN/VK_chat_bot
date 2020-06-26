import calendar
import re
import datetime

import all_flights
from generate_ticket import generate_ticket

QUANTITY_POSSIBLE_FLIGHTS = 5
QUANTITY_PLACES = 5
FORMAT_OUT_DATE = '%d-%m-%Y %H:%M'

re_date = re.compile(r'\b\d{2}-\d{2}-\d{4}\b')
re_number_date = re.compile(f'^[1-{QUANTITY_POSSIBLE_FLIGHTS}]$')
re_quantity_places = re.compile(f'^[1-{QUANTITY_PLACES}]$')
re_confirmation_booking_yes = re.compile(r'^да$')
re_confirmation_booking_no = re.compile(r'^нет$')
re_telephone = re.compile(r'^[\d\s\+\(\)\-]+$')

re_pause_yes = re.compile(r'^да$')
re_pause_no = re.compile(r'^нет$')


def handle_departures(text, context):
    for town, re_town in all_flights.RE_TOWNS.items():
        match = re.search(re_town, text)
        if match and town in all_flights.ALL_POSSIBLE_FLIGHTS:
            context['town_departure'] = town
            possible_towns = ''
            for town_arrival in all_flights.ALL_POSSIBLE_FLIGHTS[context['town_departure']]:
                possible_towns += f'{town_arrival}, '
            context['possible_towns'] = possible_towns
            return True
    else:
        return False


def handle_arrival(text, context):
    for town, re_town in all_flights.RE_TOWNS.items():
        match = re.search(re_town, text)
        if match and town in all_flights.ALL_POSSIBLE_FLIGHTS[context['town_departure']]:
            context['town_arrival'] = town
            return True
    else:
        context['town_arrival'] = text
        return False


def handle_date(text, context):
    try:
        wishful_date = datetime.datetime.strptime(text, '%d-%m-%Y').date()
        if wishful_date < datetime.date.today():
            return False
    except ValueError:
        return False

    possible_flights = dispatcher(possible_date=wishful_date,
                                  town_departure=context['town_departure'],
                                  town_arrival=context['town_arrival'])
    possible_flights_list = ''
    context_possible_flights = list()
    for i, flight in enumerate(possible_flights):
        flight_date_time = f'{calendar.day_name[flight.weekday()]}, {flight.strftime(FORMAT_OUT_DATE)}'
        possible_flights_list += f'{i + 1}. {flight_date_time}\n'
        context_possible_flights.append(flight_date_time)

    context['possible_flights_list'] = possible_flights_list
    context['possible_flights'] = context_possible_flights

    return True


def handle_number_date(text, context):
    match = re.search(re_number_date, text)
    if match:
        selected_flight = context['possible_flights'][int(text) - 1]
        context['date'] = selected_flight
        return True
    else:
        return False


def handle_quantity_places(text, context):
    match = re.search(re_quantity_places, text)
    if match:
        context['quantity_places'] = text
        return True
    else:
        return False


def handle_comment_for_booking(text, context):
    context['comment_for_booking'] = text
    return True


def handle_confirmation_booking(text, context):
    match_yes = re.search(re_confirmation_booking_yes, text)
    match_no = re.search(re_confirmation_booking_no, text)
    if match_yes:
        return True
    elif match_no:
        context['rerun'] = "Заказ билета запущен заново!"
        return True
    else:
        return False


def handle_telephone(text, context):
    match = re.search(re_telephone, text)
    if match:
        context['telephone'] = text
        return True
    else:
        return False


def handle_pause_yes(text):
    match = re.match(re_pause_yes, text)
    if match:
        return True
    else:
        return False


def handle_pause_no(text):
    match = re.match(re_pause_no, text)
    if match:
        return True
    else:
        return False


def dispatcher(possible_date, town_departure, town_arrival):
    possible_flights = set()
    flight_timetable = all_flights.ALL_POSSIBLE_FLIGHTS[town_departure][town_arrival]

    week_days = flight_timetable.get('week_days')
    month_days = flight_timetable.get('month_days')
    charter = flight_timetable.get('charter')

    date_step = datetime.timedelta(days=1)

    while len(possible_flights) < QUANTITY_POSSIBLE_FLIGHTS:
        if week_days:
            weekday = possible_date.weekday()
            if weekday in week_days:
                for time in week_days[weekday]:
                    possible_time = datetime.time(hour=time['hours'], minute=time['minutes'])
                    flight_date = datetime.datetime.combine(possible_date, possible_time)
                    if flight_date > datetime.datetime.now():
                        possible_flights.add(flight_date)
        if month_days:
            day = possible_date.day
            if day in month_days:
                for time in month_days[day]:
                    possible_time = datetime.time(hour=time['hours'], minute=time['minutes'])
                    flight_date = datetime.datetime.combine(possible_date, possible_time)
                    if flight_date > datetime.datetime.now():
                        possible_flights.add(flight_date)
        if charter:
            for flight in charter:
                flight_date = datetime.datetime.strptime(flight, FORMAT_OUT_DATE)
                if flight_date.date() == possible_date and flight_date > datetime.datetime.now():
                    possible_flights.add(flight_date)
        possible_date += date_step

    possible_flights = list(possible_flights)
    possible_flights.sort()
    possible_flights = possible_flights[:QUANTITY_POSSIBLE_FLIGHTS]

    return possible_flights


def handler_generate_ticket(text, context):
    return generate_ticket(town_departure=context['town_departure'],
                           town_arrival=context['town_arrival'],
                           date=context['date'],
                           quantity_places=context['quantity_places'],
                           comment=context['comment_for_booking'],
                           telephone=context['telephone'],
                           )
