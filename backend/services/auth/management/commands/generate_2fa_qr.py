"""
Management command: generate_2fa_qr

Generates a QR code PNG image for a user's TOTP 2FA setup.
The QR code encodes the `otpauth://` provisioning URI that
authenticator apps (Google Authenticator, Authy, etc.) can scan.

This is useful for:
- Admin-assisted 2FA enrollment (admin generates and gives the QR to the user)
- Displaying the QR code in an admin panel or printing it
- Bulk 2FA setup during onboarding

Usage:
    # Generate QR and save to a PNG file (default: media/qr_codes/{email}.png)
    python manage.py generate_2fa_qr admin@school.edu

    # Generate QR and save to a specific path
    python manage.py generate_2fa_qr admin@school.edu --output /tmp/admin_2fa.png

    # Generate QR and print as base64 to stdout (for embedding in HTML/API)
    python manage.py generate_2fa_qr admin@school.edu --to-stdout

    # Generate a new secret even if the user already has one
    python manage.py generate_2fa_qr admin@school.edu --regenerate

    # Show the raw TOTP secret in output (masked by default)
    python manage.py generate_2fa_qr admin@school.edu --show-secret
"""

import io
import base64
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from services.auth.models import User


class Command(BaseCommand):
    help = "Generate a QR code PNG for a user's TOTP 2FA setup."

    def add_arguments(self, parser):
        parser.add_argument(
            "user",
            help="Email address or UUID of the user to generate a QR code for.",
        )
        parser.add_argument(
            "--output",
            "-o",
            default=None,
            help="File path to save the QR code PNG. "
                 "Default: media/qr_codes/<email>.png",
        )
        parser.add_argument(
            "--to-stdout",
            action="store_true",
            help="Print the QR code as a base64-encoded PNG to stdout "
                 "instead of saving to a file.",
        )
        parser.add_argument(
            "--regenerate",
            action="store_true",
            help="Generate a new TOTP secret even if the user already has one.",
        )
        parser.add_argument(
            "--show-secret",
            action="store_true",
            help="Print the raw TOTP secret in the output "
                 "(masked by default for security).",
        )
        parser.add_argument(
            "--issuer",
            default=None,
            help="Issuer name shown in the authenticator app. "
                 "Default: user's school name or 'EduSphere SMS'.",
        )

    def handle(self, *args, **options):
        import pyotp
        import qrcode

        # ── Resolve user ──────────────────────────────────────────────────
        user_input = options["user"]
        try:
            user = User.objects.get(email=user_input)
        except User.DoesNotExist:
            try:
                user = User.objects.get(id=user_input)
            except (User.DoesNotExist, ValueError):
                raise CommandError(
                    f"User not found: '{user_input}'. "
                    f"Provide an email address or UUID."
                )

        self.stdout.write(f"User:      {user.full_name} <{user.email}> [{user.role}]")

        # ── Secret ────────────────────────────────────────────────────────
        if options["regenerate"] or not user.two_factor_secret:
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            user.two_factor_enabled = False  # Must verify before enabling
            user.save(update_fields=["two_factor_secret", "two_factor_enabled"])
            secret_status = "newly generated"
        else:
            secret = user.two_factor_secret
            secret_status = "existing (use --regenerate to rotate)"

        if options.get("show_secret"):
            self.stdout.write(f"Secret:    {secret} ({secret_status})")
        else:
            self.stdout.write(
                f"Secret:    {secret[:4]}...{secret[-4:]} "
                f"({secret_status}, use --show-secret to reveal)"
            )

        # ── Provisioning URI ──────────────────────────────────────────────
        issuer = options["issuer"] or getattr(user.school, "name", None) or "EduSphere SMS"
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user.email, issuer_name=issuer)

        self.stdout.write(f"Issuer:    {issuer}")
        self.stdout.write(f"URI:       {provisioning_uri}")

        # ── Generate QR code ──────────────────────────────────────────────
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # ── Output ────────────────────────────────────────────────────────
        if options["to_stdout"]:
            # Base64-encoded PNG to stdout
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            self.stdout.write(f"\nBase64 PNG ({len(b64)} chars):")
            self.stdout.write(b64)
            self.stdout.write(
                self.style.SUCCESS(
                    "\nEmbed this in an <img> tag:\n"
                    f'<img src="data:image/png;base64,{b64}" '
                    f'alt="2FA QR Code for {user.email}" />'
                )
            )
        else:
            # Save to file
            output_path = options["output"]
            if output_path is None:
                qr_dir = Path(settings.MEDIA_ROOT) / "qr_codes"
                qr_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(qr_dir / f"{user.email}.png")

            img.save(output_path, format="PNG")
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ QR code saved to: {output_path}")
            )
            self.stdout.write(
                f"File size: {Path(output_path).stat().st_size} bytes"
            )
            self.stdout.write(
                "\nNext steps:\n"
                f"  1. Share {output_path} with {user.email}\n"
                f"  2. Have them scan it with their authenticator app\n"
                f"  3. Then verify with a TOTP code to enable 2FA"
            )
