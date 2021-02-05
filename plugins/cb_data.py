import asyncio
import os

from plugins.sub_functions import view_thumbnail, delete_thumbnail, close_button
from plugins.help import help_me, start_bot
from plugins.gen_ss import generate_screen_shot


from pyrogram import (Client, InlineKeyboardButton, InlineKeyboardMarkup, ContinuePropagation, InputMediaDocument,
                      InputMediaVideo, InputMediaAudio)

from helper.ffmfunc import duration
from helper.ytdlfunc import downloadvideocli, downloadaudiocli
from translation import Translation

config_path = os.path.join(os.getcwd(), 'config.py')
if os.path.isfile(config_path):
    from config import Config
else:
    from sample_config import Config

@Client.on_callback_query()
async def catch_youtube_fmtid(c, m):

    cb_data = m.data
    if cb_data.startswith("ytdata||"):
        yturl = cb_data.split("||")[-1]
        format_id = cb_data.split("||")[-2]
        media_type = cb_data.split("||")[-3].strip()
        print(media_type)
        if media_type == 'audio':
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Audio", callback_data=f"{media_type}||{format_id}||{yturl}"), InlineKeyboardButton("Document",
                                                                                                    callback_data=f"docaudio||{format_id}||{yturl}")]])
        else:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Video", callback_data=f"{media_type}||{format_id}||{yturl}"), InlineKeyboardButton("Document",
                                                                                                    callback_data=f"docvideo||{format_id}||{yturl}")]])

        await m.edit_message_reply_markup(buttons)

    else:
        raise ContinuePropagation


@Client.on_callback_query()
async def catch_youtube_dldata(c, q):
    thumb_image_path = os.getcwd() + "/" + "thumbnails" + "/" + str(q.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        thumb_image_path = None
    file_name = str(Config.PRE_FILE_TXT)
    cb_data = q.data
    # Callback Data Check (for Youtube formats)
    if cb_data.startswith(("video", "audio", "docaudio", "docvideo")):
        yturl = cb_data.split("||")[-1]
        format_id = cb_data.split("||")[-2]
        if not cb_data.startswith(("video", "audio", "docaudio", "docvideo")):
            print("no data found")
            raise ContinuePropagation
        new_filext = "%(title)s.%(ext)s"
        filext = file_name + new_filext
        saved_file_path = os.path.join(os.getcwd(), "downloads", str(q.message.chat.id))
        if not os.path.isdir(saved_file_path):
            os.makedirs(saved_file_path)
        dl_folder = [f for f in os.listdir(saved_file_path)]
        for f in dl_folder:
            try:
                os.remove(os.path.join(saved_file_path, f))
            except IndexError:
                pass
        await q.edit_message_text(text=Translation.DOWNLOAD_START)
        filepath = os.path.join(saved_file_path, filext)

        audio_command = [
            "youtube-dl",
            "-c",
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", format_id,
            "-o", filepath,
            yturl,

        ]

        video_command = [
            "youtube-dl",
            "-c",
            "--embed-subs",
            "-f", f"{format_id}+bestaudio",
            "-o", filepath,
            "--hls-prefer-ffmpeg", yturl]

        loop = asyncio.get_event_loop()

        med = None
        if cb_data.startswith("audio"):
            filename = await downloadaudiocli(audio_command)
            med = InputMediaAudio(
                media=filename,
                caption=os.path.basename(filename),
                title=os.path.basename(filename),
                thumb=thumb_image_path
            )

        if cb_data.startswith("video"):
            filename = await downloadvideocli(video_command)
            dur = round(duration(filename))
            med = InputMediaVideo(
                media=filename,
                duration=dur,
                caption=os.path.basename(filename),
                thumb=thumb_image_path,
                supports_streaming=True
            )

        if cb_data.startswith("docaudio"):
            filename = await downloadaudiocli(audio_command)
            med = InputMediaDocument(
                media=filename,
                caption=os.path.basename(filename),
                thumb=thumb_image_path
            )

        if cb_data.startswith("docvideo"):
            filename = await downloadvideocli(video_command)
            dur = round(duration(filename))
            med = InputMediaDocument(
                media=filename,
                caption=os.path.basename(filename),
                thumb=thumb_image_path
            )

        if med:
            loop.create_task(send_file(c, q, med))

        else:
            print("med not found")

    else:
        # Callback Data Check (for bot settings)
        if cb_data.startswith(("help", "view_thum", "del_thum", "close", "start",)):
            if cb_data.startswith("help"):
                await help_me(c, q)
            if cb_data.startswith("close"):
                await close_button(c, q)
            if cb_data.startswith("del_thumb"):
                await delete_thumbnail(c, q)
            if cb_data.startswith("view_thumb"):
                await view_thumbnail(c, q)
            if cb_data.startswith("start"):
                await start_bot(c, q)


async def send_file(c, q, med):
    try:
        await q.edit_message_text(text=Translation.UPLOAD_START)
        await c.send_chat_action(chat_id=q.message.chat.id, action="upload_document")
        await q.edit_message_media(media=med)
        await generate_screen_shot(c, q)
    except IndexError as e:
        print(e)
