import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIMES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ


def _allowed_extension(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _detect_mime(header: bytes):
    """Определяет MIME по первым байтам файла (magic numbers)."""
    signatures = {
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'\xff\xd8\xff':        'image/jpeg',
        b'GIF87a':              'image/gif',
        b'GIF89a':              'image/gif',
        b'RIFF':                'image/webp',
    }
    for sig, mime in signatures.items():
        if header.startswith(sig):
            return mime
    return None


def validate_upload(file_storage):
    """
    Проверяет файл перед сохранением.
    Возвращает (ok: bool, error: str | None).
    """
   
    if file_storage is None:
        return True, None

    filename = getattr(file_storage, 'filename', None)
    if not filename:  
        return True, None  

    original = secure_filename(filename)

    
    if not _allowed_extension(original):
        return False, 'Недопустимое расширение. Разрешены: png, jpg, jpeg, gif, webp'

    
    if hasattr(file_storage, 'file') and file_storage.file is not None:
        header = file_storage.file.read(512)
        file_storage.file.seek(0)
    else:
        value = getattr(file_storage, 'value', b'') or b''
        header = value[:512]

    mime = _detect_mime(header)
    if mime not in ALLOWED_MIMES:
        return False, 'Файл не является изображением'

    
    if hasattr(file_storage, 'file') and file_storage.file is not None:
        file_storage.file.seek(0, os.SEEK_END)
        size = file_storage.file.tell()
        file_storage.file.seek(0)
    else:
        value = getattr(file_storage, 'value', b'') or b''
        size = len(value)

    if size > MAX_FILE_SIZE:
        return False, 'Файл больше 5 МБ'

    return True, None


def safe_filename(original: str) -> str:
    """Генерирует безопасное имя с UUID и валидным расширением."""
    original = secure_filename(original)
    if '.' in original:
        ext = original.rsplit('.', 1)[1].lower()
    else:
        ext = 'bin'
    if ext not in ALLOWED_EXTENSIONS:
        ext = 'bin'
    return f"{uuid.uuid4().hex}.{ext}"