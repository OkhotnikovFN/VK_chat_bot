import datetime
import unittest
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from vk_api.bot_longpoll import VkBotMessageEvent
import time_machine

from avia_ticket_bot import ChatBot
from tests import settings_for_test_avia_ticket_bot


class TestChatBot(TestCase):
    RAW_EVENT_NEW = {'type': 'message_new',
                     'object': {'message': {'date': 1589237812, 'from_id': 2917161, 'id': 883, 'out': 0,
                                            'peer_id': 2917161, 'text': 'Проверка', 'conversation_message_id': 865,
                                            'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
                                            'is_hidden': False},
                                'client_info': {
                                    'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link'],
                                    'keyboard': True, 'inline_keyboard': True, 'lang_id': 0}},
                     'group_id': 195072517, 'event_id': '947af626a2d47a40f372a18ae4e445c410594572'}

    def test_run(self):
        count = 5
        event = VkBotMessageEvent(raw=self.RAW_EVENT_NEW)
        events = [event] * count

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('avia_ticket_bot.vk_api.VkApi'):
            with patch('avia_ticket_bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
                bot = ChatBot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(event=event)
                self.assertEqual(bot.on_event.call_count, count)

    def test_run(self):
        count = 5
        event = VkBotMessageEvent(raw=self.RAW_EVENT_NEW)
        events = [event] * count

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('avia_ticket_bot.vk_api.VkApi'):
            with patch('avia_ticket_bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
                bot = ChatBot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(event=event)
                self.assertEqual(bot.on_event.call_count, count)

    INPUTS = settings_for_test_avia_ticket_bot.INPUTS
    EXPECTED_OUTPUTS = settings_for_test_avia_ticket_bot.EXPECTED_OUTPUTS

    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT_NEW)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        time_now = time_machine.travel(datetime.datetime(year=2020, month=5, day=25))
        time_now.start()

        with patch('avia_ticket_bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
            bot = ChatBot('', '')
            bot.api = api_mock
            bot.run()

        time_now.stop()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS


if __name__ == '__main__':
    unittest.main()
