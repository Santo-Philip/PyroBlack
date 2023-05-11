import os
import tempfile
from typing import Union, AsyncGenerator

import pyrogram
from pyrogram import types
from pyrogram.file_id import FileId


class StreamMediaMod:

    async def streamer(
        self,
        message: Union["types.Message", str],
        chunk_size: int = 10240,
        delete_folder: bool = False,
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
            media = message

       
        if media is None:
            raise ValueError("This message doesn't contain any downloadable media")

      
        if isinstance(media, str):
            file_id_str = media
        else:
            file_id_str = media.file_id

       
        file_id_obj = FileId.decode(file_id_str)

       
        file_size = getattr(media, "file_size", 0)

        
        tmp_file = tempfile.NamedTemporaryFile(delete=False)

      
        offset = 0
        while True:
            chunk = await self.client.download_media(file_id_obj, offset=offset, limit=chunk_size)
            if not chunk:
                break
         
            yield chunk

            del chunk
            offset += chunk_size

        tmp_file.close()

        if delete_folder:
            try:
                os.rmdir(tmp_file.name)
            except OSError:
                pass
