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

            chunks = math.ceil(file_size / (5 * 1024 * 1024))
            offset += chunks

        temp_dir = tempfile.mkdtemp()

        try:
            # Iterate over the chunks of the file, writing each chunk to a temporary file in the temporary directory.
            async with tempfile.TemporaryDirectory() as temp_dir:
                for i in range(0, file_size, 5 * 1024 * 1024):
                    with open(os.path.join(temp_dir, f"{i}.chunk"), "wb") as f:
                        f.write(await self.get_file(file_id_obj, file_size, limit, offset + i))

                    # Open the temporary file and read its contents.
                    with open(os.path.join(temp_dir, f"{i}.chunk"), "rb") as f:
                        yield f.read()

                    # Remove the temporary file.
                    os.remove(os.path.join(temp_dir, f"{i}.chunk"))

            # Iterate over the chunks of the file, doing something with each chunk.
            async for chunk in (chunk for i, chunk in self.get_file(file_id_obj, file_size, limit, offset)):
                # Do something with the chunk.
                pass

        finally:
            # Remove the temporary directory and all files in it
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                os.remove(file_path)
            os.rmdir(temp_dir)
