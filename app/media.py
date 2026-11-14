"""Saving and finding uploaded photos on disk.

Photos are not public files: they are served only through an endpoint that
checks the viewer belongs to the couple. On disk each photo gets a random
name, so nobody can guess it, and the user's original file name is ignored.
"""

import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings

MAX_PHOTO_BYTES = 10 * 1024 * 1024  # 10 MB


def _detect_image(head: bytes) -> tuple[str, str] | None:
    """Look at the first bytes of the file ("magic numbers") to see what it really is.

    The file name and the Content-Type sent by the client can be anything,
    so they are not trusted.
    """
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg", "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp", "image/webp"
    if head[4:12] in (b"ftypheic", b"ftypheix", b"ftyphevc", b"ftypmif1"):
        return ".heic", "image/heic"  # iPhone photos
    return None


def photos_dir() -> Path:
    path = Path(settings.media_dir) / "memories"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_photo(upload: UploadFile) -> tuple[str, str]:
    """Check and store one uploaded photo. Returns (file name on disk, content type)."""
    data = upload.file.read(MAX_PHOTO_BYTES + 1)
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"{upload.filename}: a photo can be at most 10 MB",
        )
    kind = _detect_image(data[:16])
    if kind is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"{upload.filename}: only JPEG, PNG, WEBP and HEIC photos are allowed",
        )
    extension, content_type = kind
    filename = secrets.token_hex(16) + extension
    (photos_dir() / filename).write_bytes(data)
    return filename, content_type


def photo_path(filename: str) -> Path:
    return photos_dir() / filename


def delete_photo_file(filename: str) -> None:
    photo_path(filename).unlink(missing_ok=True)
