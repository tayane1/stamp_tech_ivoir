from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import QRCode


@shared_task
def check_expiring_qr_codes():
    """Vérifie les QR codes qui expirent dans 7 jours"""
    from datetime import timedelta

    expiring_soon = QRCode.objects.filter(
        status=QRCode.Status.ACTIVE,
        expires_at__lte=timezone.now() + timedelta(days=7),
        expires_at__gte=timezone.now(),
    ).select_related("user", "company")

    for qr in expiring_soon:
        send_mail(
            subject=f"Votre QR code {qr.unique_code} expire bientôt",
            message=f"Bonjour,\n\nVotre QR code expire le {qr.expires_at.strftime('%d/%m/%Y')}.",
            from_email="noreply@stamptech.ci",
            recipient_list=[qr.user.email],
        )

    return f"{expiring_soon.count()} alertes envoyées"


@shared_task
def mark_expired_qr_codes():
    """Marque les QR codes expirés"""
    expired = QRCode.objects.filter(
        status=QRCode.Status.ACTIVE, expires_at__lt=timezone.now()
    ).update(status=QRCode.Status.EXPIRED)

    return f"{expired} QR codes marqués comme expirés"


@shared_task
def generate_daily_report():
    """Génère un rapport quotidien"""
    from apps.audit.models import AuditLog
    from datetime import timedelta

    yesterday = timezone.now() - timedelta(days=1)

    stats = {
        "qr_generated": AuditLog.objects.filter(
            action=AuditLog.Action.QR_GENERATED, created_at__date=yesterday.date()
        ).count(),
        "qr_verified": AuditLog.objects.filter(
            action=AuditLog.Action.QR_VERIFIED, created_at__date=yesterday.date()
        ).count(),
    }

    # Envoyer rapport par email aux admins
    send_mail(
        subject=f"Rapport quotidien - {yesterday.strftime('%d/%m/%Y')}",
        message=f'QR générés: {stats["qr_generated"]}\nQR vérifiés: {stats["qr_verified"]}',
        from_email="noreply@stamptech.ci",
        recipient_list=["admin@stamptech.ci"],
    )

    return stats


@shared_task
def backup_database():
    """Sauvegarde la base de données"""
    import subprocess
    from datetime import datetime

    backup_file = f'/backups/stamptech_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'

    subprocess.run(
        [
            "pg_dump",
            "-h",
            "localhost",
            "-U",
            "postgres",
            "-d",
            "stamptech",
            "-f",
            backup_file,
        ]
    )

    return f"Backup créé: {backup_file}"
