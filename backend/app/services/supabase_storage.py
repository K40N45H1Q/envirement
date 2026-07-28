import mimetypes
from pathlib import PurePosixPath
from secrets import token_hex

from fastapi import HTTPException, UploadFile

from app.services.supabase_client import get_supabase_client


UPLOADS_BUCKET = "uploads"


def ensure_uploads_bucket() -> None:
    client = get_supabase_client()
    try:
        client.storage.get_bucket(UPLOADS_BUCKET)
    except Exception:
        client.storage.create_bucket(UPLOADS_BUCKET, options={"public": True})


def upload_file(upload: UploadFile, folder: str, prefix: str | None = None) -> str:
    ensure_uploads_bucket()
    original_filename = PurePosixPath(upload.filename or "upload").name
    name_prefix = f"{prefix}_" if prefix else ""
    object_path = f"{folder}/{name_prefix}{token_hex(8)}_{original_filename}"
    content_type = upload.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

    try:
        upload.file.seek(0)
        file_bytes = upload.file.read()
        get_supabase_client().storage.from_(UPLOADS_BUCKET).upload(
            path=object_path,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "false",
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"key": "file_upload_failed"}) from exc

    return get_supabase_client().storage.from_(UPLOADS_BUCKET).get_public_url(object_path)


def remove_file(file_url: str | None) -> None:
    if not file_url:
        return

    marker = f"/storage/v1/object/public/{UPLOADS_BUCKET}/"
    if marker not in file_url:
        return

    object_path = file_url.split(marker, 1)[1].split("?", 1)[0]
    if not object_path:
        return

    try:
        get_supabase_client().storage.from_(UPLOADS_BUCKET).remove([object_path])
    except Exception:
        pass
