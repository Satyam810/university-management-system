"""QR code generation utilities."""
import qrcode
import io
import base64
from django.conf import settings


def generate_qr_code(session_id: str, valid_until: str) -> str:
    """
    Generate QR code as base64 string for embedding in HTML.
    QR contains session_id and validity info.
    """
    data = f"UMS_ATTENDANCE:{session_id}:{valid_until}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()
