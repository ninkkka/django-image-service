from typing import Any, Optional

class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[dict] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

class ImageNotFoundException(AppException):
    def __init__(self, image_id: str):
        super().__init__(
            status_code=404,
            detail=f"Изображение с ID {image_id} не найдено"
        )

class OCRProcessingException(AppException):
    def __init__(self, detail: str = "Ошибка при обработке OCR"):
        super().__init__(status_code=422, detail=detail)

class EmailSendingException(AppException):
    def __init__(self, detail: str = "Ошибка при отправке email"):
        super().__init__(status_code=422, detail=detail)

class DjangoAPIException(AppException):
    def __init__(self, detail: str = "Ошибка при обращении к Django API"):
        super().__init__(status_code=502, detail=detail)