import os
import tempfile
from typing import Union, Optional, BinaryIO

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId


class StreamMediaMod:
    async def streamer(
        self: "pyrogram.Client",
        message: Union["types.Message", str],
        file_path: Optional[str] = None,
        limit: int = 0,
        offset: int = 0,
    ) -> Optional[Union[str, BinaryIO]]:
        available_media = (
            "audio",
            "document",
            "photo",
            "sticker",
            "animation",
            "video",
            "voice",
            "video_note",
            "new_chat_photo",
        )

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

            min_chunk_size = 10240  # 10KB
            max_chunk_size = 10485760  # 10MB
            chunks = max(min_chunk_size, min(max_chunk_size, file_size // 100))
            offset += chunks

        # Use the specified file path or create a temporary file
        if file_path is None:
            _, file_path = tempfile.mkstemp()

        try:
            with open(file_path, "wb") as f:
                async for chunk in self.iter_file(file_id_obj, file_size, limit, offset):
                    f.write(chunk)
                    yield chunk

        except Exception:
            # Delete the file if an exception occurs
            os.remove(file_path)
            raise

        else:
            # Close the file
            f.close()
