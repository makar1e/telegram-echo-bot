# -*- coding: utf-8 -*-
import json
import telebot
from telebot import types
import keep_alive.js

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный от BotFather
TOKEN = '7174202587:AAFTulD-6fVqj-h-2an4hv8Ao4wCaXd8gJ0'
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /accept
@bot.message_handler(commands=['accept'])
def accept_user(message):
    # Разделяем аргументы команды
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Неверное количество аргументов. Используйте: /accept User_ID")
        return

    user_id = args[0]
    # Проверяем, что User_ID является числом
    if not user_id.isdigit():
        bot.reply_to(message, "User_ID должен быть числом.")
        return

    # Отправляем сообщение пользователю
    try:
        bot.send_message(user_id, "Вы приняты в группу!")
        bot.reply_to(message, "Сообщение успешно отправлено.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отправке сообщения: {e}")



# Создаем словарь для хранения анкет пользователей
user_profiles = {}

# Функция для загрузки анкет из файла
def load_profiles_from_file():
    global user_profiles
    try:
        with open('user_profiles.json', 'r', encoding='utf-8') as file:
            user_profiles = json.load(file)
    except FileNotFoundError:
        user_profiles = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    load_profiles_from_file()  # Загружаем анкеты из файла перед началом работы
    bot.send_message(message.chat.id, "Главное меню")
    create_profile_button(message)

# Функция для создания кнопок
def create_profile_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Создать анкету', 'Показать мою анкету')
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)




# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    if message.text == 'Создать анкету':
        if user_id in user_profiles:
            bot.send_message(message.chat.id, "Вы уже создали анкету. Если хотите изменить ее, нажмите 'Показать мою анкету'.")
        else:
            user_profiles[user_id] = {}
            bot.send_message(message.chat.id, "Введите ваше имя:")
            bot.register_next_step_handler(message, get_name)
    elif message.text == 'Показать мою анкету':
        show_profile(message)
    elif message.text == 'Подать заявку на вступление в группу':
        apply_for_group(message)
        
# Список User_ID специальных людей
special_users = ['1162099746', '1266502380']  # Замените на реальные User_ID


# Функция для подачи заявки на вступление в группу
def apply_for_group(message):
    user_id = message.from_user.id
    # Проверяем, есть ли анкета у пользователя
    if user_id not in user_profiles:
        bot.send_message(message.chat.id, "У вас нет анкеты. Создайте её, нажав на кнопку 'Создать анкету'.")
        return
    # Отправляем сообщение специальным людям
    for special_user in special_users:
        bot.send_message(special_user, f"Пользователь {user_id} подал заявку на вступление в группу.")
    # Отправляем сообщение пользователю о том, что его заявка подана
    bot.send_message(user_id, "Ваша заявка подана. Вы будете уведомлены о результате.")
    # Создаем кнопки главного меню
    create_profile_button(message)

# Функция для создания кнопок
def create_profile_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Создать анкету', 'Показать мою анкету', 'Подать заявку на вступление в группу')
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Получаем имя пользователя
def get_name(message):
    user_id = message.from_user.id
    name = message.text
    user_profiles[user_id]['name'] = name
    bot.send_message(message.chat.id, "Введите ваш возраст:")
    bot.register_next_step_handler(message, get_age)

# Получаем возраст пользователя
def get_age(message):
    user_id = message.from_user.id
    age = message.text
    if age.isdigit():
        user_profiles[user_id]['age'] = int(age)
        bot.send_message(message.chat.id, "Введите ваш никнейм в Telegram через @:")
        bot.register_next_step_handler(message, get_telegram_username)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите возраст цифрами.")
        bot.register_next_step_handler(message, get_age)

# Получаем никнейм пользователя в Telegram
def get_telegram_username(message):
    user_id = message.from_user.id
    telegram_username = message.text
    
    # Проверяем, начинается ли никнейм с "@"
    if telegram_username.startswith('@'):
        user_profiles[user_id]['telegram_username'] = telegram_username
        bot.send_message(message.chat.id, "Отправьте ваше фото:")
        bot.register_next_step_handler(message, get_photo)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите никнейм в Telegram через @.")
        bot.register_next_step_handler(message, get_telegram_username)
        

# Получаем фото пользователя
def get_photo(message):
    user_id = message.from_user.id
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        user_profiles[user_id]['photo'] = downloaded_file
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фото.")
        bot.register_next_step_handler(message, get_photo)
        return
    bot.send_message(message.chat.id, "Напишите краткое описание (до 500 символов):")
    bot.register_next_step_handler(message, get_description)


# Получаем описание пользователя
def get_description(message):
    user_id = message.from_user.id
    description = message.text
    if len(description) > 500:
        bot.send_message(message.chat.id, "Описание слишком длинное. Пожалуйста, сократите его до 500 символов.")
        bot.register_next_step_handler(message, get_description)
        return
    user_profiles[user_id]['description'] = description
    confirm_profile(message)
    
# Функция для сохранения анкет в файл
def save_profiles_to_file():
    with open('user_profiles.json', 'w', encoding='utf-8') as file:
        json.dump(user_profiles, file, ensure_ascii=False, indent=4)

# Подтверждение анкеты пользователя
def confirm_profile(message):
    user_id = message.from_user.id
    user_profile = user_profiles[user_id]
    photo_file = user_profile['photo']
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Подтвердить', 'Отменить')
    bot.send_photo(message.chat.id, photo_file, caption="Ваша анкета готова:\n\n"
                                                        f"Имя: {user_profile['name']}\n"
                                                        f"Возраст: {user_profile['age']}\n"
                                                        f"Никнейм: {user_profile['telegram_username']}\n"
                                                        f"Описание: {user_profile['description']}\n\n"
                                                        "Подтвердите её создание или отмените.",
                   reply_markup=markup)
    bot.register_next_step_handler(message, finalize_profile)

# Окончательная обработка анкеты пользователя
def finalize_profile(message):
    user_id = message.from_user.id
    user_profile = user_profiles[user_id]
    if message.text == 'Подтвердить':
        bot.send_message(message.chat.id, "Анкета подтверждена.")
        print(f"Создана новая анкета для пользователя с ID: {user_id}")
        print(f"Никнейм: {user_profile['telegram_username']}")
        print(f"Имя: {user_profile['name']}")
        print(f"Возраст: {user_profile['age']}")
        print(f"Описание: {user_profile['description']}")
        bot.send_message(message.chat.id, "Перенаправление в главное меню.")
        create_profile_button(message)
    elif message.text == 'Отменить':
        bot.send_message(message.chat.id, "Анкета отменена.")
        bot.send_message(message.chat.id, "Перенаправление в главное меню.")
        create_profile_button(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для подтверждения или отмены анкеты.")



# Отображение анкеты пользователя
def show_profile(message):
    user_id = message.from_user.id
    if user_id in user_profiles:
        user_profile = user_profiles[user_id]
        photo_file = user_profile['photo']
        bot.send_photo(message.chat.id, photo_file, caption="Ваша анкета:\n\n"
                                                            f"Имя: {user_profile['name']}\n"
                                                            f"Возраст: {user_profile['age']}\n"
                                                            f"Никнейм: {user_profile['telegram_username']}\n"
                                                            f"Описание: {user_profile['description']}\n")
    else:
        bot.send_message(message.chat.id, "У вас нет анкеты. Создайте её, нажав на кнопку 'Создать анкету'.")
        
        



# Запуск бота
bot.polling(none_stop=True)

