import math
import os
import shutil
import tempfile
from typing import Union, Optional, BinaryIO

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId


class StreamMediaMod:
    async def streamer(self, message, limit=0, offset=0):
        available_media = (
        "audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note", "new_chat_photo")

        if isinstance(message, types.Message):
            for kind in available_media:
                media = getattr(message, kind, None)

                if media is not None:
                    break
            else:
                raise ValueError("This message doesn't contain any downloadable media")
        else:
            media = message

        if isinstance(media, str):
            file_id_str = media
        else:
            file_id_str = media.file_id

        file_id_obj = FileId.decode(file_id_str)
        file_size = getattr(media, "file_size", 0)

        if offset < 0:
            if file_size == 0:
                raise ValueError("Negative offsets are not supported for file ids, pass a Message object instead")

            chunks = math.ceil(file_size / (5 * 1024 * 1024))
            offset += chunks

        # Download each chunk to a temporary directory one by one and delete each chunk immediately after it is accessed or read
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                chunk_index = 0
                for chunk in await self.get_file(file_id_obj, file_size, limit, offset):
                    with open(os.path.join(temp_dir, str(chunk_index)), "wb") as f:
                        f.write(chunk)
                    chunk_index += 1

                chunks = []
                for chunk in os.listdir(temp_dir):
                    with open(os.path.join(temp_dir, chunk), "rb") as f:
                        chunks.append(f.read())

                return chunks
            except Exception as e:
                # Delete the temporary directory if any error occurs
                shutil.rmtree(temp_dir)
                raise e
