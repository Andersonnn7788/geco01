"""Notification helpers for booking confirmations."""
from __future__ import annotations

import asyncio
import base64
from datetime import datetime
from typing import Optional

from app.config import get_settings
from app.services.supabase import get_supabase_service

try:
    from fpdf import FPDF  # type: ignore

    PDF_ENABLED = True
except Exception:
    PDF_ENABLED = False

try:
    import resend  # type: ignore

    RESEND_AVAILABLE = True
except Exception:
    resend = None  # type: ignore
    RESEND_AVAILABLE = False


def _format_datetime(iso_str: str) -> str:
    """Format ISO datetime strings into a readable local string."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y %I:%M %p")
    except Exception:
        return iso_str


def _build_booking_pdf(booking: dict, user_profile: Optional[dict]) -> Optional[bytes]:
    """Create a simple booking confirmation PDF."""
    if not PDF_ENABLED:
        return None

    space = booking.get("spaces") or {}
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Booking Confirmation", ln=1)

    pdf.set_font("Helvetica", "", 11)
    summary_lines = [
        f"Booking ID: {booking.get('id', '')}",
        f"Guest: {user_profile.get('full_name') or user_profile.get('email') or 'Guest'}",
        f"Email: {user_profile.get('email', '')}" if user_profile else "",
        f"Space: {space.get('name', '')}",
        f"Location: {space.get('location', '') or 'Kuala Lumpur'}",
        f"Date: {_format_datetime(booking.get('start_time', ''))}",
        f"End: {_format_datetime(booking.get('end_time', ''))}",
        f"Attendees: {booking.get('attendees_count', '')}",
        f"Total Paid: RM{float(booking.get('total_amount', 0) or 0):.2f}",
        f"Status: {booking.get('status', '').capitalize() or 'Confirmed'}",
    ]

    pdf.ln(4)
    for line in summary_lines:
        if not line:
            continue
        pdf.multi_cell(0, 8, line)

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Thank you for choosing Infinity8. Please present this confirmation upon arrival.",
    )

    return pdf.output(dest="S").encode("latin-1")


def _send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    attachment: Optional[bytes],
    attachment_name: str,
) -> None:
    """Send an email with an optional attachment via Resend."""
    settings = get_settings()
    if not (settings.RESEND_API_KEY and settings.RESEND_FROM):
        raise RuntimeError("Resend configuration is missing; cannot send email.")
    if not RESEND_AVAILABLE:
        raise RuntimeError("Resend SDK not installed; cannot send email.")

    resend.api_key = settings.RESEND_API_KEY

    attachments = []
    if attachment:
        attachments.append(
            {
                "filename": attachment_name,
                "content": base64.b64encode(attachment).decode("utf-8"),
                "encoding": "base64",
            }
        )

    html_body = "<br>".join(body.splitlines())

    resend.Emails.send(
        {  # Resend expects base64 + encoding for binary attachments
            "from": settings.RESEND_FROM,
            "to": [to_email],
            "subject": subject,
            "text": body,
            "html": html_body,
            "attachments": attachments or None,
        }
    )


async def send_booking_confirmation_email(
    booking_id: str,
    fallback_email: Optional[str] = None,
) -> None:
    """
    Build a PDF receipt for a booking and email it to the user.

    Idempotent: skips sending if payment receipt_url is already marked as sent.
    """
    settings = get_settings()
    if not settings.RESEND_API_KEY or not settings.RESEND_FROM:
        print("Resend not configured; skipping booking confirmation email.")
        return
    if not RESEND_AVAILABLE:
        print("Resend SDK not installed; skipping booking confirmation email.")
        return

    supabase = get_supabase_service()
    booking = await supabase.get_booking_by_id(booking_id)
    if not booking:
        print(f"Booking {booking_id} not found; cannot send confirmation email.")
        return

    payment = await supabase.get_payment_by_booking(booking_id)
    if payment and payment.get("receipt_url") == "email_sent":
        # Already sent a confirmation for this booking
        return

    user_profile = await supabase.get_user_profile(booking.get("user_id", ""))
    recipient = (user_profile or {}).get("email") or fallback_email
    if not recipient:
        print(f"No email available for booking {booking_id}; skipping send.")
        return

    space = booking.get("spaces") or {}
    date_label = _format_datetime(booking.get("start_time", ""))
    subject = f"Booking confirmed: {space.get('name', 'Your space')} on {date_label}"

    body_lines = [
        f"Hi {user_profile.get('full_name') or 'there'},",
        "",
        "Your booking is confirmed. Details:",
        f"- Space: {space.get('name', '')}",
        f"- Location: {space.get('location', '') or 'Kuala Lumpur'}",
        f"- Starts: {date_label}",
        f"- Ends: {_format_datetime(booking.get('end_time', ''))}",
        f"- Attendees: {booking.get('attendees_count', '')}",
        f"- Amount: RM{float(booking.get('total_amount', 0) or 0):.2f}",
        "",
        "The confirmation PDF is attached. We look forward to hosting you!",
        "",
        "-- Infinity8 Team",
    ]
    body = "\n".join(body_lines)

    pdf_bytes = _build_booking_pdf(booking, user_profile or {})
    attachment_name = f"booking-{booking_id}.pdf"

    try:
        await asyncio.to_thread(
            _send_email_with_attachment,
            recipient,
            subject,
            body,
            pdf_bytes,
            attachment_name,
        )
    except Exception as exc:
        print(f"Failed to send booking confirmation email for {booking_id}: {exc}")
        return

    # Mark payment record to avoid duplicate sends
    if payment:
        try:
            await supabase.update_payment_status(
                booking_id=booking_id,
                payment_status=payment.get("payment_status", "completed"),
                transaction_id=payment.get("transaction_id"),
                receipt_url=payment.get("receipt_url") or "email_sent",
            )
        except Exception as exc:
            print(f"Warning: could not mark confirmation email as sent ({booking_id}): {exc}")
