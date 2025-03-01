import asyncio
import json
from configparser import ConfigParser
import mysql.connector
import pika
import base64
from telebot import TeleBot
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo
from telebot.types import InputMediaAudio


# Loading the config file
config = ConfigParser()
config.read('config.ini')

# MIME types and related media input classes
mime_types = {
    'image/png': InputMediaPhoto,
    'image/jpeg': InputMediaPhoto,
    'image/webp': InputMediaPhoto,
    'image/gif': InputMediaPhoto,
    'video/mp4': InputMediaVideo,
    'audio/mpeg': InputMediaAudio,
}

def callback(ch, method, properties, body):
    body_dict = json.loads(body)

    # Connecting to MySQL
    db = mysql.connector.connect(
        host=config.get(section='DATABASE', option='host'),
        port=config.getint(section='DATABASE', option='port'),
        database=config.get(section='DATABASE', option='database'),
        user=config.get(section='DATABASE', option='user'),
        password=config.get(section='DATABASE', option='password'),
    )
    cursor = db.cursor()

    # Loading an integration
    cursor.execute(
        operation='SELECT bot_token, chat_id FROM telegram_messages WHERE id=%(id)s LIMIT 1;',
        params={'id': body_dict['integration_id']}
    )

    record = cursor.fetchone()
    db.close()

    if record is not None:
        bot = TeleBot(token=record[0])

        # Filtering attachments with relevant MIME types
        attachments = tuple(filter(
            lambda file_data: file_data['mime'] in mime_types and len(file_data['body']) < 50 * (1024 * 1024),
            body_dict['attachments']
        ))

        if len(attachments) > 0:
            if len(attachments) > 1:
                media = [
                    mime_types[file['mime']](
                        media=base64.b64decode(file['body']),
                        caption=body_dict['text']
                    ) for file in attachments
                ]
                bot.send_media_group(chat_id=record[1], media=media)
            else:
                file_data = attachments[0]
                if file_data['mime'] in ('image/png', 'image/jpeg', 'image/webp', 'image/gif'):
                    image_data = base64.b64decode(file_data['body'])
                    bot.send_photo(chat_id=record[1], photo=image_data, caption=body_dict['text'])
                elif file_data['mime'] in ('video/mp4',):
                    video_data = base64.b64decode(file_data['body'])
                    bot.send_video(chat_id=record[1], video=video_data, caption=body_dict['text'])
                elif file_data['mime'] in ('audio/mpeg',):
                    audio_data = base64.b64decode(file_data['body'])
                    bot.send_audio(chat_id=record[1], audio=audio_data, caption=body_dict['text'])
        else:
            if body_dict['text'] is not None:
                bot.send_message(chat_id=record[1], text=body_dict['text'])

    ch.basic_ack(delivery_tag=method.delivery_tag)
# callback


if __name__ == '__main__':
    rabbit_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.get(section='RABBIT', option='host'),
            port=config.getint(section='RABBIT', option='port'),
            credentials=pika.PlainCredentials(
                username=config.get(section='RABBIT', option='user'),
                password=config.get(section='RABBIT', option='password'),
            ),
        )
    )

    rabbit_channel = rabbit_connection.channel()

    rabbit_channel.queue_declare(
        queue=config.get(section='APP', option='queue_tg_message'),
        durable=True,
    )
    rabbit_channel.basic_qos(prefetch_count=1)

    rabbit_channel.basic_consume(
        queue=config.get(section='APP', option='queue_tg_message'),
        on_message_callback=callback
    )

    rabbit_channel.start_consuming()
