import os
import shutil

from pyrogram import InputMediaPhoto
from helper.gen_ss_help import generate_screen_shots
from plugins.trim_video import trim

config_path = os.path.join(os.getcwd(), 'config.py')
if os.path.isfile(config_path):
    from config import Config
else:
    from sample_config import Config

async def generate_screen_shot(client, update):
    await client.send_chat_action(chat_id=update.message.chat.id, action="upload_document")
    tmp_directory_for_each_user = os.path.join(os.getcwd(), "screenshots", str(update.from_user.id))
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    saved_file_path = os.path.join(os.getcwd(), "downloads", str(update.message.chat.id))
    for file in os.listdir(saved_file_path):
        dir_content = (os.path.join(saved_file_path, file))
        if dir_content is not None:
            images = await generate_screen_shots(
                dir_content,
                tmp_directory_for_each_user,
                5,
                9
            )
            media_album_p = []
            if images is not None:
                i = 0
                caption = str(Config.PRE_FILE_TXT)
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode="html"
                                )
                            )
                        else:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await client.send_chat_action(chat_id=update.message.chat.id, action="upload_photo")
            await client.send_media_group(
                chat_id=update.message.chat.id,
                disable_notification=True,
                reply_to_message_id=update.message.message_id,
                media=media_album_p
            )
            try:
                shutil.rmtree(tmp_directory_for_each_user)
                await trim(client, update)
            except IndexError:
                pass
