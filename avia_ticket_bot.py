import random
import logging.config

import requests
import vk_api
import vk_api.bot_longpoll
from pony.orm import db_session

import avia_settings
import all_flights
import avia_handlers
from models import UserState, Booking

try:
    import self_settings
except ImportError:
    exit('DO cp self_settings.py.default self_settings.py and set token and group_id')

from avia_log_settings import log_config

logging.config.dictConfig(log_config)
log = logging.getLogger('avia_bot')


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

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event=event)
            except Exception:
                log.exception("Ошибка в обработке события")

    @db_session
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
        state = UserState.get(user_id=user_id)

        scenario_stop_pause = self.check_stop_pause_scenario(text=text, state=state, user_id=user_id)
        if not scenario_stop_pause:
            self.check_intent_and_scenario(text=text, user_id=user_id, state=state)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 30),
            peer_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 30),
            peer_id=user_id)

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(avia_handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)

    def check_intent_and_scenario(self, text, user_id, state):
        for intent in avia_settings.INTENTS:
            if text.lower() == intent['tokens']:
                log.debug(f'User gets {intent}')
                if intent['answer']:
                    text_to_send = intent['answer']
                    if state:
                        text_to_send += avia_settings.SCENARIOS_PAUSE['wish_to_continue']
                        state.pause = True
                    self.send_text(text_to_send, user_id)
                else:
                    if state:
                        text_to_send = avia_settings.DEFAULT_ANSWER
                        text_to_send += avia_settings.SCENARIOS_PAUSE['wish_to_continue']
                        state.pause = True
                        self.send_text(text_to_send, user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                break
        else:
            if state:
                self.continue_scenario(text, state, user_id)
            else:
                self.send_text(avia_settings.DEFAULT_ANSWER, user_id)

    def check_stop_pause_scenario(self, text, state, user_id):

        check_stop_pause = False
        if state:
            if text.lower() == avia_settings.STOP_SCENARIO['token']:
                state.delete()
                self.send_text(avia_settings.STOP_SCENARIO['answer'], user_id)
                check_stop_pause = True
            elif state.pause:
                self.pause_scenario(text, state, user_id)
                check_stop_pause = True

        return check_stop_pause

    def pause_scenario(self, text, state, user_id):
        handler_yes = avia_handlers.handle_pause_yes(text=text.lower())
        handler_no = avia_handlers.handle_pause_no(text=text.lower())
        if handler_yes:
            steps = avia_settings.SCENARIOS[state.scenario_name]['steps']
            step = steps[state.step_name]
            self.send_step(step, user_id, text, state.context)
            state.pause = False
        elif handler_no:
            self.send_text(avia_settings.SCENARIOS_PAUSE['end_of_scenario'], user_id)
            state.delete()
        else:
            self.send_text(avia_settings.SCENARIOS_PAUSE['continue_or_not'], user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = avia_settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        init_context = {'towns_departures': all_flights.towns_departures,
                        'towns_arrival': all_flights.towns_arrival
                        }
        self.send_step(step, user_id, text, init_context)
        UserState(user_id=user_id, scenario_name=scenario_name, step_name=first_step, context=init_context, pause=False)

    def continue_scenario(self, text, state, user_id):
        steps = avia_settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(avia_handlers, step['handler'])
        if handler(text=text.lower(), context=state.context):
            self.next_step(state=state, steps=steps, step=step, user_id=user_id, text=text)
        else:
            self.retry_current_step(state=state, steps=steps, step=step, user_id=user_id)


    def next_step(self, state, steps, step, user_id, text):
        rerun_text = state.context.get('rerun')
        if rerun_text:
            state.step_name = avia_settings.SCENARIOS[state.scenario_name]['first_step']
            step = avia_settings.SCENARIOS[state.scenario_name]['steps'][state.step_name]
            text_to_send = f'{rerun_text}\n{step["text"].format(**state.context)}'
            self.send_text(text_to_send, user_id)
            state.context['rerun'] = None
            return
        next_step = steps[step['next_step']]
        self.send_step(next_step, user_id, text, state.context)
        if next_step['next_step']:
            # switch to next step
            state.step_name = step['next_step']
        else:
            # finish scenario
            log.info(
                "from: {town_departure}, to: {town_arrival}, date: {date}, quantity_places: {quantity_places}, "
                "comment: {comment_for_booking}, telephone: {telephone}.".format(**state.context))
            Booking(town_departure=state.context['town_departure'],
                    town_arrival=state.context['town_arrival'],
                    date=state.context['date'],
                    quantity_places=state.context['quantity_places'],
                    comment=state.context['comment_for_booking'],
                    telephone=state.context['telephone'])
            state.delete()

    def retry_current_step(self, state, steps, step, user_id):
        text_to_send = step['failure_text'].format(**state.context)
        self.send_text(text_to_send, user_id)
        if not step['failure_next_step']:
            state.delete()
        else:
            if step['failure_next_step'] != state.step_name:
                next_step = steps[step['failure_next_step']]
                text_to_send += f'\n{next_step["text"].format(**state.context)}'
                self.send_text(text_to_send, user_id)
                if next_step['next_step']:
                    # switch to next step
                    state.step_name = step['next_step']
                else:
                    # finish scenario
                    state.delete()


if __name__ == '__main__':
    log.debug('Запуск бота')
    bot = ChatBot(group_id=self_settings.GROUP_ID, token=self_settings.TOKEN)
    bot.run()
