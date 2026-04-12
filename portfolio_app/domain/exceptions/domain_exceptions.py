"""domain/exceptions/domain_exceptions.py — Uygulama exception hiyerarşisi."""


class DomainException(Exception):
    """Tüm domain exception'larının tabanı."""


class ValidationError(DomainException):
    """Geçersiz alan değeri veya iş kuralı ihlali."""


class NotFoundError(DomainException):
    """İstenen kayıt bulunamadı."""


class DuplicateError(DomainException):
    """Benzersiz olması gereken bir kayıt zaten mevcut."""


class StorageError(DomainException):
    """Dosya sistemi / görsel depolama hatası."""


class DatabaseError(DomainException):
    """Veritabanı işlem hatası."""
