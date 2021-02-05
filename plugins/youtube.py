import os
import time
from translation import Translation
from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton
from helper.ytdlfunc import extractYt, create_buttons
from plugins.help import help_me

config_path = os.path.join(os.getcwd(), 'config.py')
if os.path.isfile(config_path):
    from config import Config
else:
    from sample_config import Config

ytregex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(Filters.regex(ytregex))
async def ytdl(_, message):
    if message.from_user.id not in Config.AUTH_USERS:
        await _.delete_messages(chat_id=message.chat.id, message_ids=message.message_id)
        a = await message.reply_text(text=Translation.NOT_AUTH_TXT, disable_web_page_preview=True)
        time.sleep(5)
        await a.delete()
        await help_me(_, message)
        return
    url = message.text.strip()
    await message.delete()
    await message.reply_chat_action("typing")
    try:
        title, thumbnail_url, formats = extractYt(url)
    except Exception:
        await message.delete()
        await message.reply_text(
            text=Translation.FAILED_LINK,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
        )
        return
    buttons = InlineKeyboardMarkup(list(create_buttons(formats)))
    sentm = await message.reply_text(text=Translation.PROCESS_START)
    try:
        # Todo add webp image support in thumbnail by default not supported by pyrogram
        # https://www.youtube.com/watch?v=lTTajzrSkCw
        await message.reply_photo(thumbnail_url, caption=title, reply_markup=buttons)
        await sentm.delete()
    except Exception as e:
        try:
            thumbnail_url = "https://telegra.ph/file/ce37f8203e1903feed544.png"
            await message.reply_photo(thumbnail_url, caption=title, reply_markup=buttons)
            await sentm.delete()
        except Exception as e:
            await sentm.edit(f"<code>{e}</code> #Error")
