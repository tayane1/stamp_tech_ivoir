"""
Core utilities
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class UUIDGenerator:
    """Utility for generating UUIDs."""

    @staticmethod
    def generate_uuid():
        """Generate a random UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_uuid_with_prefix(prefix):
        """Generate UUID with prefix."""
        return f"{prefix}_{uuid.uuid4()}"


class CodeGenerator:
    """Utility for generating various codes."""

    @staticmethod
    def generate_random_code(length=6, digits_only=True):
        """Generate random code."""
        if digits_only:
            return "".join(random.choices(string.digits, k=length))
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def generate_alphanumeric_code(length=8):
        """Generate alphanumeric code."""
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_backup_codes(count=10, length=8):
        """Generate backup codes."""
        return [CodeGenerator.generate_alphanumeric_code(length) for _ in range(count)]


class TimeUtils:
    """Utility for time operations."""

    @staticmethod
    def get_expiration_time(hours=24):
        """Get expiration time from now."""
        return timezone.now() + timedelta(hours=hours)

    @staticmethod
    def is_expired(timestamp):
        """Check if timestamp is expired."""
        return timezone.now() > timestamp

    @staticmethod
    def get_time_until_expiration(timestamp):
        """Get time until expiration."""
        if TimeUtils.is_expired(timestamp):
            return None
        return timestamp - timezone.now()


class EmailService:
    """Service for email operations."""

    @staticmethod
    def send_notification_email(to_email, subject, message):
        """Send notification email."""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(user, verification_code):
        """Send verification email."""
        subject = "Email Verification"
        message = f"""
        Hello {user.get_full_name() or user.email},
        
        Please use the following code to verify your email:
        
        Verification Code: {verification_code}
        
        This code will expire in 24 hours.
        
        Best regards,
        Stamp Team
        """

        return EmailService.send_notification_email(user.email, subject, message)


class FileUtils:
    """Utility for file operations."""

    @staticmethod
    def get_file_extension(filename):
        """Get file extension."""
        return filename.split(".")[-1].lower() if "." in filename else ""

    @staticmethod
    def is_valid_image_extension(extension):
        """Check if extension is valid for images."""
        valid_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
        return extension.lower() in valid_extensions

    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate unique filename."""
        extension = FileUtils.get_file_extension(original_filename)
        unique_id = uuid.uuid4().hex[:8]
        return f"{unique_id}.{extension}" if extension else unique_id


class ValidationUtils:
    """Utility for validation operations."""

    @staticmethod
    def is_valid_email(email):
        """Validate email format."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_phone(phone):
        """Validate phone number format."""
        import re

        # Basic phone validation - can be customized
        pattern = r"^\+?1?\d{9,15}$"
        return re.match(pattern, phone) is not None

    @staticmethod
    def is_strong_password(password):
        """Check if password is strong."""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special


class PaginationUtils:
    """Utility for pagination."""

    @staticmethod
    def get_pagination_info(page, page_size, total_count):
        """Get pagination information."""
        total_pages = (total_count + page_size - 1) // page_size

        return {
            "current_page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
