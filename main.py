import telebot
import requests
import fitz
from PIL import Image

TOKEN = '7033003079:AAESA-GrE27JfHALeC_Ngb2XsrM537S2ph0'
bot = telebot.TeleBot(TOKEN)

def crop_schedule(image_path, coordinates):
    image = Image.open(image_path)
    area = (coordinates['x'], coordinates['y'], coordinates['x'] + coordinates['w'], coordinates['y'] + coordinates['h'])
    cropped_image = image.crop(area)
    cropped_image.save(image_path)

@bot.message_handler(func=lambda message: True)
def send_schedule(message):
    if message.text.startswith('/r'):  # Проверяем, что сообщение начинается с команды /r
        date = message.text[3:]  # Получаем дату из сообщения после /r
        date_split = date.split('.')
        day = date_split[0]
        month = date_split[1]

        url = f'https://mkeiit.ru/wp-content/uploads/2024/{month}/{day}.{month}.2024.pdf'
        response = requests.get(url)

        if response.status_code == 200:
            with open(f'{day}.{month}.pdf', 'wb') as f:
                f.write(response.content)

            pdf_document = fitz.open(f'{day}.{month}.pdf')
            last_page = pdf_document[-1]

            last_page_png = last_page.get_pixmap()
            last_page_png.save(f'{day}.{month}.png', 'png')

            coordinates = {'x': 3, 'y': 175, 'w': 340, 'h': 220}  # Укажите координаты для обрезки
            crop_schedule(f'{day}.{month}.png', coordinates)  # Обрезаем расписание

            with open(f'{day}.{month}.png', 'rb') as f:
                bot.send_photo(message.chat.id, f)
        else:
            bot.reply_to(message, f"Расписание на {day}.{month} не найдено.")
    else:
        bot.reply_to(message, "Для получения расписания введите команду в формате /r дата.месяц")

bot.polling()