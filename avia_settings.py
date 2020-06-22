STOP_SCENARIO = {
    'token': '/stop',
    'answer': 'Заказ был остановлен'
}

INTENTS = [
    {
        "name": "Помощь",
        "tokens": "/help",
        "scenario": None,
        "answer": f"Здравствуйте, я бот который поможет вам заказать билет на самолет, чтобы начать заказ, "
                  f"введите команду /ticket, вызвать эту команду можно командой /help, "
                  f"чтобы остановить заказ введите {STOP_SCENARIO['token']}"
    },
    {
        "name": "Заказ билета",
        "tokens": "/ticket",
        "scenario": "booking",
        "answer": None
    }
]

SCENARIOS_PAUSE = {
    'wish_to_continue': '\n\n Желаете продолжить заказ билета?',
    'end_of_scenario': 'Вы завершили сценарий',
    'continue_or_not': "Пожалуйста введите 'да' или 'нет'"
}

SCENARIOS = {
    "booking": {
        "first_step": "step1",
        "steps": {
            "step1": {
                "text": "Вы начали сценарий заказа авиа-билетов, чтобы начать заказ билета введите город отправления.",
                "failure_text": "Рейсы возможны из городов:\n{towns_departures}\nв города:\n{towns_arrival}.",
                "handler": "handle_departures",
                "next_step": "step2",
                "failure_next_step": "step1"
            },
            "step2": {
                "text": "Из города {town_departure} возможны рейсы в города:\n"
                        "{possible_towns}\n"
                        "Введите город прибытия",
                "failure_text": "Из города {town_departure}, нет рейсов в город '{town_arrival}', "
                                "извините заказ билетоа окончен, для повторной попытки наберите команду /ticket.",
                "handler": "handle_arrival",
                "next_step": "step3",
                "failure_next_step": None
            },
            "step3": {
                "text": "Введите желаемую дату рейса в формате число-месяц-год (12-05-2020).",
                "failure_text": "Пожалуйста введите реальную дату в указанном формате число-месяц-год (12-05-2020).",
                "handler": "handle_date",
                "next_step": "step4",
                "failure_next_step": "step3"
            },
            "step4": {
                "text": "Ближайшие рейсы {town_departure} - {town_arrival}:\n{possible_flights_list}",
                "failure_text": "Введите номер даты полета из предложенных:"
                                "Ближайшие рейсы {town_departure} - {town_arrival}:\n{possible_flights_list}",
                "handler": "handle_number_date",
                "next_step": "step5",
                "failure_next_step": "step4"
            },
            "step5": {
                "text": "Введите колличество мест (от 1 до 5).",
                "failure_text": "Пожалуйста введите необходимое колличесвто мест (от 1 до 5).",
                "handler": "handle_quantity_places",
                "next_step": "step6",
                "failure_next_step": "step5"
            },
            "step6": {
                "text": "Введите комментарий к заказу в произвольной форме.",
                "failure_text": "",
                "handler": "handle_comment_for_booking",
                "next_step": "step7",
                "failure_next_step": "step6"
            },
            "step7": {
                "text": "Проверьте введенные данные:\n"
                        "Город отправления: {town_departure}\n"
                        "Город назначения: {town_arrival}\n"
                        "Дата вылета: {date}\n"
                        "Количество мест: {quantity_places}\n"
                        "Ваш комметарий: {comment_for_booking}\n"
                        "если данные верны на пишите 'да', "
                        "если есть ошибка напишите 'нет' и заказ начнется заново.",
                "failure_text": "Пожалуйста, напишите 'да' или 'нет.'",
                "handler": "handle_confirmation_booking",
                "next_step": "step8",
                "failure_next_step": "step7"
            },
            "step8": {
                "text": "Введите ваш номер телефона, по которому с вами свяжутся для подтверждения заказа.",
                "failure_text": "Номер телефона может содержать любые цифры, а так же: пробел, -, +, ().",
                "handler": "handle_telephone",
                "next_step": "step9",
                "failure_next_step": "step8"
            },
            "step9": {
                "text": "Спасибо, ваш заказ будет обработан, с вами свяжутся по номеру {telephone}.",
                "failure_text": None,
                "handler": None,
                "next_step": None,
                "failure_next_step": None
            },
        }
    }
}

DEFAULT_ANSWER = INTENTS[0]['answer']
