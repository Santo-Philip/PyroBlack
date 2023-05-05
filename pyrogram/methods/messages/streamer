import tempfile
import os
from typing import Union, Optional, BinaryIO

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

            min_chunk_size = 10240  # 10KB
            max_chunk_size = 10485760  # 10MB
            chunks = max(min_chunk_size, min(max_chunk_size, file_size // 100))
            offset += chunks

        # Create a temporary directory to store the downloaded chunks
        with tempfile.TemporaryDirectory() as tempdir:
            chunk_files = []
            try:
                async for chunk in self.get_file(file_id_obj, file_size, limit, offset):
                    # Write each chunk to a temporary file
                    chunk_filename = os.path.join(tempdir, f"{len(chunk_files):08d}")
                    with open(chunk_filename, "wb") as f:
                        f.write(chunk)
                    chunk_files.append(chunk_filename)

                    # Yield the chunk
                    with open(chunk_filename, "rb") as f:
                        yield f

            finally:
                # Delete the chunk files
                for chunk_filename in chunk_files:
                    os.remove(chunk_filename)
