import math
import os
from typing import Union, Optional, BinaryIO
import tempfile

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId


class StreamMediaMod:
    async def streamer(
        self: "pyrogram.Client",
        message: Union["types.Message", str],
        limit: int = 0,
        offset: int = 0
    ) -> Optional[Union[str, BinaryIO]]:
        available_media = ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note",
                           "new_chat_photo")

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

            chunks = math.ceil(file_size / 1024 / 1024)
            offset += chunks

        temp_dir = tempfile.mkdtemp()

        try:
            for i, chunk in enumerate(self.get_file(file_id_obj, file_size, limit, offset)):
                with open(os.path.join(temp_dir, f"{i}.chunk"), "wb") as f:
                    f.write(chunk)
                yield f.read()
                os.remove(f.name)
        finally:
            # Remove the temporary directory and all files in it
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                os.remove(file_path)
            os.rmdir(temp_dir)
