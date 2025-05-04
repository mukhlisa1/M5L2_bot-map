import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

user_style_selection = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '''Доступные команды:  
        /show_city <city_name> - показать карту с городом
        /remember_city <city_name> - сохранить город в базе данных
        /show_my_cities - показать все сохраненные города
        /set_style <color> <marker> <line_style> - установить стиль карты''')
    # Допиши команды бота


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    user_id = message.chat.id

    map_path = f'{user_id}_city_map.png'
    if manager.draw_city_region_map(map_path, city_name):
        with open(map_path, 'rb') as map_file:
            bot.send_photo(user_id, map_file, caption=f" Карта города {city_name}")
    else:
        bot.send_message(user_id, "Город не найден или координаты отсутствуют.")


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)
    if cities:
        style = user_style_selection.get(user_id, {'color': 'b', 'marker': '.', 'line_style': 'None'})
        manager.create_grapf(f'{user_id}_cities.png', cities, style)
        with open(f'{user_id}_cities.png', 'rb') as map:
            bot.send_photo(user_id, map)
    else:
        bot.send_message(user_id, "У вас пока нет сохраненных городов.")

@bot.message_handler(commands=['set_style'])
def set_style_start(message):
    user_style_selection[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, "Выберите цвет маркера (например: `r`, `g`, `b`, `c`, `m`, `y`, `k`, `orange`, `purple`, `pink`):")
    bot.register_next_step_handler(msg, get_marker_color)

def get_marker_color(message):
    user_id = message.chat.id
    color = message.text.strip()
    user_style_selection[user_id]['color'] = color

    msg = bot.send_message(user_id, "Выберите маркер (`.`, `o`, `^`, `*`, `s`, `+`, `x`):")
    bot.register_next_step_handler(msg, get_marker_shape)

def get_marker_shape(message):
    user_id = message.chat.id
    marker = message.text.strip()
    user_style_selection[user_id]['marker'] = marker

    msg = bot.send_message(user_id, "Выберите стиль линии (`-`, `--`, `:`, `None`):")
    bot.register_next_step_handler(msg, get_line_style)

def get_line_style(message):
    user_id = message.chat.id
    line_style = message.text.strip()
    user_style_selection[user_id]['line_style'] = line_style

    bot.send_message(user_id, f"✅ Стиль сохранён!\n"
                              f"Цвет: {user_style_selection[user_id]['color']}\n"
                              f"Маркер: {user_style_selection[user_id]['marker']}\n"
                              f"Линия: {user_style_selection[user_id]['line_style']}")


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()