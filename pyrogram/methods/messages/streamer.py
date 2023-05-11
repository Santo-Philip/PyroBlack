import aiocontextvars
import asyncio
import math
import os
import tempfile
from typing import Union, Optional, BinaryIO
import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId

temp_dir_var = aiocontextvars.ContextVar("temp_dir")


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

        async with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_var.set(temp_dir)
            try:
                for i in range(0, file_size, 5 * 1024 * 1024):
                    with open(os.path.join(temp_dir, f"{i}.chunk"), "wb") as f:
                        f.write(await self.get_file(file_id_obj, file_size, limit, offset + i))

                    with open(os.path.join(temp_dir, f"{i}.chunk"), "rb") as f:
                        yield f.read()

                    os.remove(os.path.join(temp_dir, f"{i}.chunk"))

                async for chunk in self.get_file(file_id_obj, file_size, limit, offset):
                    pass

            finally:
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    os.unlink(file_path)
                os.rmdir(temp_dir)
                temp_dir_var.reset()
