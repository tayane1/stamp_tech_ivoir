"""
Custom exceptions for the application
"""


class StampException(Exception):
    """Base exception for Stamp application."""

    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(StampException):
    """Authentication related errors."""

    pass


class AuthorizationError(StampException):
    """Authorization related errors."""

    pass


class ValidationError(StampException):
    """Validation related errors."""

    pass


class QRCodeError(StampException):
    """QR Code related errors."""

    pass


class EncryptionError(StampException):
    """Encryption related errors."""

    pass


class NotificationError(StampException):
    """Notification related errors."""

    pass


class AuditError(StampException):
    """Audit related errors."""

    pass


class CompanyError(StampException):
    """Company related errors."""

    pass


class TwoFactorError(StampException):
    """Two-factor authentication related errors."""

    pass


class ServiceUnavailableError(StampException):
    """Service unavailable errors."""

    pass


class RateLimitError(StampException):
    """Rate limiting errors."""

    pass


class DatabaseError(StampException):
    """Database related errors."""

    pass


class ExternalServiceError(StampException):
    """External service related errors."""

    pass


class ConfigurationError(StampException):
    """Configuration related errors."""

    pass


class SecurityError(StampException):
    """Security related errors."""

    pass


class BusinessLogicError(StampException):
    """Business logic related errors."""

    pass


class FileProcessingError(StampException):
    """File processing related errors."""

    pass


class CacheError(StampException):
    """Cache related errors."""

    pass


class CeleryError(StampException):
    """Celery task related errors."""

    pass
