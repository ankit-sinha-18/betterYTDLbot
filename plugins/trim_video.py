import os
import shutil
import time
from translation import Translation
from helper.gen_ss_help import cult_small_video


async def trim(client, update):
    saved_file_path = os.path.join(os.getcwd(), "downloads", str(update.message.chat.id))
    output_directory = os.path.join(os.getcwd(), "sample_video")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    for file in os.listdir(saved_file_path):
        dir_content = (os.path.join(saved_file_path, file))
        if dir_content is not None:
            start_time = "00:00:10"
            end_time = "00:00:20"
            a = await client.send_message(text=Translation.TRIM_WAIT, chat_id=update.message.chat.id)
            o = await cult_small_video(dir_content, output_directory, start_time, end_time)
            # just wait the code to complete trimming process !
            time.sleep(30)
            await a.delete()
            await client.send_chat_action(chat_id=update.message.chat.id, action="upload_video")
            if o is not None:
                await client.send_video(
                    chat_id=update.message.chat.id,
                    video=o,
                    caption=str(Translation.TRIM_FINISH),
                    supports_streaming=True
                )
            try:
                os.remove(o)
                shutil.rmtree(saved_file_path)
                b = await client.send_message(text=Translation.THANKS_MESSAGE, chat_id=update.message.chat.id)
                time.sleep(5)
                await b.delete()
            except IndexError:
                pass
        else:
            await update.edit_message_text(text=Translation.NO_MEDIA)
