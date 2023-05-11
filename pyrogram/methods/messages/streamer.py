import tempfile
from typing import Union, AsyncGenerator

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId


class StreamMediaMod:


    async def streamer(
            self: "pyrogram.Client",
            message: Union["types.Message", str],
            chunk_size: int = 10240,
    ) -> AsyncGenerator[bytes, None]:
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
            file_id_str = media.id

        file_id_obj = FileId.decode(file_id_str)
        file_size = getattr(media, "file_size", 0)

        # Create a temporary file.
        tmp_file = tempfile.NamedTemporaryFile(delete=False)

        # Start downloading the media in chunks.
        offset = 0
        while True:
            chunk = await self.download_media(file_id_obj)
            if not chunk:
                break
            # Yield the chunk.
            yield chunk
            # Delete the chunk.
            del chunk
            offset += chunk_size

        # Close the temporary file.
        tmp_file.close()
