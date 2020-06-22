import random
import logging.config

import vk_api
import vk_api.bot_longpoll

import avia_settings
import all_flights
import avia_handlers

try:
    import self_settings
except ImportError:
    exit('DO cp self_settings.py.default self_settings.py and set token and group_id')

from avia_log_settings import log_config

logging.config.dictConfig(log_config)
log = logging.getLogger('avia_bot')


class UserState:
    """Состояние пользователя внутри сценария."""

    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.pause = False
        self.context = context or {'towns_departures': all_flights.towns_departures,
                                   'towns_arrival': all_flights.towns_arrival
                                   }


class ChatBot:
    """
    Сценарий заказа авиабилетов на самолет через vk.com

    Поддерживает команды
    /ticket — начинает сценарий заказа билетов;
    /help — выдает справку о том, как работает робот.

    Use python3.7
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, group_id)

        self.api = self.vk.get_api()
        self.user_states = dict()  # user_id -> UserState

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event=event)
            except Exception:
                log.exception("Ошибка в обработке события")

    def on_event(self, event: vk_api.bot_longpoll.VkBotEventType):
        """
        Отправляет сообщение назад, если это текст.

        :param event: VkBotMessageEvent obj
        :return: None
        """
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info(f'Мы пока не умеем обрабатывать события типа {event.type}')
            return

        user_id = event.message.peer_id
        text = event.message.text

        text_to_send = self.check_stop_pause_scenario(text=text, user_id=user_id)
        if not text_to_send:
            text_to_send = self.check_intent_and_scenario(text=text, user_id=user_id)

        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 30),
            peer_id=user_id)

    def check_intent_and_scenario(self, text, user_id):
        for intent in avia_settings.INTENTS:
            if text.lower() == intent['tokens']:
                log.debug(f'User gets {intent}')
                if intent['answer']:
                    text_to_send = intent['answer']
                    if user_id in self.user_states:
                        text_to_send += avia_settings.SCENARIOS_PAUSE['wish_to_continue']
                        self.user_states[user_id].pause = True
                else:
                    text_to_send = self.start_scenario(user_id, intent['scenario'])
                break
        else:
            if user_id in self.user_states:
                text_to_send = self.continue_scenario(user_id, text)
            else:
                text_to_send = avia_settings.DEFAULT_ANSWER
        return text_to_send

    def check_stop_pause_scenario(self, text, user_id):

        text_to_send = None

        if user_id in self.user_states:

            if text.lower() == avia_settings.STOP_SCENARIO['token']:
                self.user_states.pop(user_id)
                text_to_send = avia_settings.STOP_SCENARIO['answer']
            elif self.user_states[user_id].pause:
                text_to_send = self.pause_scenario(user_id, text)

        return text_to_send

    def pause_scenario(self, user_id, text):
        handler_yes = avia_handlers.handle_pause_yes(text=text.lower())
        handler_no = avia_handlers.handle_pause_no(text=text.lower())
        if handler_yes:
            state = self.user_states[user_id]
            steps = avia_settings.SCENARIOS[state.scenario_name]['steps']
            step = steps[state.step_name]
            text_to_send = step["text"].format(**state.context)
            self.user_states[user_id].pause = False
        elif handler_no:
            text_to_send = avia_settings.SCENARIOS_PAUSE['end_of_scenario']
            self.user_states.pop(user_id)
        else:
            text_to_send = avia_settings.SCENARIOS_PAUSE['continue_or_not']
        return text_to_send

    def start_scenario(self, user_id, scenario_name):
        scenario = avia_settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = avia_settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(avia_handlers, step['handler'])
        if handler(text=text.lower(), context=state.context):
            text_to_send = self.next_step(state=state, steps=steps, step=step, user_id=user_id)
        else:
            text_to_send = self.retry_current_step(state=state, steps=steps, step=step, user_id=user_id)

        return text_to_send

    def next_step(self, state, steps, step, user_id):
        rerun_text = state.context.get('rerun')
        if rerun_text:
            state.step_name = avia_settings.SCENARIOS[state.scenario_name]['first_step']
            step = avia_settings.SCENARIOS[state.scenario_name]['steps'][state.step_name]
            text_to_send = f'{rerun_text}\n{step["text"].format(**state.context)}'
            state.context['rerun'] = None
            return text_to_send
        next_step = steps[step['next_step']]
        text_to_send = next_step['text'].format(**state.context)
        if next_step['next_step']:
            # switch to next step
            state.step_name = step['next_step']
        else:
            # finish scenario
            log.info(
                "from: {town_departure}, to: {town_arrival}, date: {date}, quantity_places: {quantity_places}, "
                "comment: {comment_for_booking}, telephone: {telephone}.".format(**state.context))
            self.user_states.pop(user_id)

        return text_to_send

    def retry_current_step(self, state, steps, step, user_id):
        text_to_send = step['failure_text'].format(**state.context)
        if not step['failure_next_step']:
            self.user_states.pop(user_id)
        else:
            if step['failure_next_step'] != state.step_name:
                next_step = steps[step['failure_next_step']]
                text_to_send += f'\n{next_step["text"].format(**state.context)}'
                if next_step['next_step']:
                    # switch to next step
                    state.step_name = step['next_step']
                else:
                    # finish scenario
                    self.user_states.pop(user_id)
        return text_to_send


if __name__ == '__main__':
    log.debug('Запуск бота')
    bot = ChatBot(group_id=self_settings.GROUP_ID, token=self_settings.TOKEN)
    bot.run()
