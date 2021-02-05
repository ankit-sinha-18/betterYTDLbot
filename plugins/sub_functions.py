import os
import os.path
import time
from pyrogram import (Client, InlineKeyboardButton, InlineKeyboardMarkup, Filters)
from translation import Translation
from plugins.help import help_me

config_path = os.path.join(os.getcwd(), 'config.py')
if os.path.isfile(config_path):
    from config import Config
else:
    from sample_config import Config


@Client.on_message(Filters.photo)
async def save_photo(client, update):
    # received single photo
    if update.from_user.id not in Config.AUTH_USERS:
        await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
        a = await update.message.reply_text(text=Translation.NOT_AUTH_TXT, disable_web_page_preview=True)
        time.sleep(5)
        await a.delete()
        await help_me(client, update)
        return
    await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
    thumb_image = os.getcwd() + "/" + "thumbnails" + "/" + str(update.from_user.id) + ".jpg"
    await client.download_media(message=update, file_name=thumb_image)
    await update.delete()
    await client.send_message(
        chat_id=update.message.chat.id,
        text=Translation.SAVED_CUSTOM_THUMB_NAIL,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back", callback_data="help")]
            ])
    )


async def view_thumbnail(client, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
        c = await update.message.reply_text(text=Translation.NOT_AUTH_TXT, disable_web_page_preview=True)
        time.sleep(5)
        await c.delete()
        await help_me(client, update)
        return
    await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
    thumb_image = os.getcwd() + "/" + "thumbnails" + "/" + str(update.from_user.id) + ".jpg"
    if os.path.exists(thumb_image):
        await client.send_photo(
            chat_id=update.message.chat.id,
            photo=thumb_image,
            caption=Translation.THUMB_CAPTION,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("DEL THUMB", callback_data="del_thumb"),
                     InlineKeyboardButton("Back", callback_data="help")]
                ])
        )

    else:
        await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
        d = await client.send_message(chat_id=update.message.chat.id, text=Translation.NO_THUMB)
        time.sleep(5)
        await d.delete()


async def delete_thumbnail(client, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
        e = await update.message.reply_text(text=Translation.NOT_AUTH_TXT, disable_web_page_preview=True)
        time.sleep(5)
        await e.delete()
        await help_me(client, update)
        return
    await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
    thumb_image_path = os.getcwd() + "/" + "thumbnails" + "/"
    media_files = os.listdir(thumb_image_path)
    if len(media_files) == 0:
        f = await client.send_message(chat_id=update.message.chat.id, text=Translation.NO_THUMB)
        time.sleep(5)
        await f.delete()
    else:
        thumb_image = os.getcwd() + "/" + "thumbnails" + "/" + str(update.from_user.id)
        if os.path.exists(thumb_image):
            try:
                os.remove(thumb_image + ".jpg")
                await client.send_message(
                    chat_id=update.message.chat.id,
                    text=Translation.DEL_CUSTOM_THUMB_NAIL,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Back", callback_data="help")]
                        ])
                )
            except IndexError:
                pass


async def close_button(client, update):
    await client.delete_messages(chat_id=update.message.chat.id, message_ids=update.message.message_id)
