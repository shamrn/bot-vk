import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
import random
import logging

log = logging.getLogger('vk_bot')
def configure_logging():
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))  #формат лога время,уровень,сообщение
    log.addHandler(file_handler)
    file_handler.setLevel(logging.DEBUG)




class Bot:
    """
    Bot play cities for vk.com
    Use python 3.9

    """

    def __init__(self, token, group_id):

        self.vk_session = vk_api.VkApi(
            token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.vk = self.vk_session.get_api()

        self.communication = {
            'to_welcome': ['привет', 'салам', 'здарова', 'ку', 'hi', 'hello'],
            'how_you': ['как дела', 'как твои дела', 'как настроение', 'как ты', 'how are you', 'ты как'],
            'game_challenge': ['города', 'играть в города', 'играть', 'играем', 'город', 'начать', 'старт'],
            'city_location': ['где находится', 'это где', 'где это', 'это где?', 'где это?', 'местоположение',
                              "где это ?"],
            'to_stop': ['стоп', 'все', 'прервать', 'остановить'],
            'info_city': ['инфо', 'информация', '?']
        }

        self.status_user = {}

    def run(self):
        """Запуск бота,обработка сообщений"""

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.user_msg = event.object.message['text'].lower()
                self.user_id = event.object.message['peer_id']

                log.debug(f'id - {self.user_id} message - {self.user_msg}  status - {self.status_user}')

                if self.user_msg in self.communication['game_challenge']:
                    self.status_user[self.user_id] = {'status': 1, 'bot_cities': None, 'user_cities': None,
                                                      'named_cities': []}

                elif self.user_msg in self.communication['to_welcome']:
                    self.send_msg('Привет,мы с тобой можем поиграть в города')

                elif self.user_msg in self.communication['how_you']:
                    self.send_msg('У меня все отлично,почему мы еще не играем в города?')

                elif self.user_id not in self.status_user:
                    self.send_msg('Не разобрал твое сообщение,напиши "начать" и мы с тобой начнем играть в города')

                if self.user_id in self.status_user:
                    if self.user_msg == '' or self.user_msg == ' ':
                        self.send_msg('Не разобрал твое сообщение')
                    elif self.user_msg in self.communication['city_location']:
                        self.send_msg(
                            'https://www.google.ru/maps/place/' + self.status_user[self.user_id]['bot_cities'])
                    elif self.user_msg in self.communication['to_stop']:
                        self.send_msg('Слабовато')
                        del self.status_user[self.user_id]
                    else:
                        self.send_msg(self.city_game())



    def send_msg(self, text):
        """Отправка сообщение пользователю"""
        self.text = text
        self.vk.messages.send(user_id=self.user_id, message=self.text, random_id=0,keyboard=open('keyboard.json', 'r', encoding='UTF-8').read())

    def city_game(self):
        """Цикл игры в города"""

        with open('city.txt', 'r', encoding='utf-8') as text:
            lst = []
            for city in text:
                lst.append(city.lower())
        lst_city = [word.strip() for word in lst]

        letters_exception = ')', 'ь', 'ъ', 'ы'

        def last_letter(city):
            """Функция проверяет последние буквы слова на буквы и символы
                в списке исключений 'letters_exception, и выдает одну букву для проверки'"""
            last_letter = -1 if city[-1] not in letters_exception else -2
            if city[last_letter] in letters_exception:
                last_letter = -3
            return city[last_letter]

        if self.status_user[self.user_id]['status'] == 1:
            self.bot_cities = random.choice(lst_city)
            self.status_user[self.user_id]['named_cities'] += self.bot_cities.split()
            self.status_user[self.user_id]['bot_cities'] = self.bot_cities
            self.status_user[self.user_id]['status'] = 2
            return self.bot_cities.title()

        elif self.status_user[self.user_id]['status'] > 1:
            self.status_user[self.user_id]['user_cities'] = self.user_msg.lower()

            if last_letter(self.status_user[self.user_id]['bot_cities']) == \
                    self.status_user[self.user_id]['user_cities'][0] \
                    and self.status_user[self.user_id]['user_cities'] not in self.status_user[self.user_id][
                'named_cities'] \
                    and self.status_user[self.user_id]['user_cities'] in lst_city:
                self.status_user[self.user_id]['named_cities'] += self.status_user[self.user_id]['user_cities'].split()
                self.status_user[self.user_id]['status'] += 1

                if self.status_user[self.user_id]['status'] == 4:
                    self.send_msg('Я могу подсказать где находится город,просто напиши "где это"')

                while True:
                    self.bot_cities = random.choice(lst_city)
                    if self.bot_cities[0] == last_letter(self.status_user[self.user_id]['user_cities']) \
                            and self.bot_cities not in self.status_user[self.user_id]['named_cities']:
                        break

                log.debug(f'user id - {self.user_id} bot cities - {self.bot_cities}')

                self.status_user[self.user_id]['named_cities'] += self.bot_cities.split()
                self.status_user[self.user_id]['bot_cities'] = self.bot_cities
                return self.bot_cities.title()

            elif self.status_user[self.user_id]['user_cities'] in self.status_user[self.user_id]['named_cities']:
                return 'Такой город был, тебе на букву:' + last_letter(self.status_user[self.user_id]['bot_cities'])

            else:
                return 'Попробуй еще раз, тебе на букву:' + last_letter(self.status_user[self.user_id]['bot_cities'])




if __name__ == "__main__":
    configure_logging()
    bot = Bot(TOKEN, ID)
    bot.run()
