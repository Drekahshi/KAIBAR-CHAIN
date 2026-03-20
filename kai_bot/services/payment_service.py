"""
payment_service.py
──────────────────────────────────────────────────────────────────
KAIBAR Payment Service
Handles X402 QR generation and M-Pesa Daraja STK Push.
"""
from __future__ import annotations
import os
import base64
import httpx
from datetime import datetime
from typing import Optional

# ── M-Pesa config ──────────────────────────────────────────────
MPESA_CONSUMER_KEY    = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE       = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY         = os.getenv("MPESA_PASSKEY", "")
MPESA_CALLBACK_URL    = os.getenv("MPESA_CALLBACK_URL", "https://kaibar.app/api/payments/mpesa/callback")
MPESA_BASE_URL        = "https://sandbox.safaricom.co.ke"

# ── M-Pesa helpers ──────────────────────────────────────────────

async def get_mpesa_token() -> Optional[str]:
    if not MPESA_CONSUMER_KEY or not MPESA_CONSUMER_SECRET:
        return None
    auth = base64.b64encode(
        f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(
                f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {auth}"},
            )
            if res.status_code == 200:
                return res.json().get("access_token")
    except Exception:
        pass
    return None


async def initiate_stk_push(phone: str, amount: int, account_ref: str, description: str) -> dict:
    """Trigger M-Pesa STK push on Safaricom Daraja sandbox."""
    token = await get_mpesa_token()
    if not token:
        # Return a mock response for demo when keys not configured
        return {
            "success": True,
            "mode": "demo",
            "message": "STK push simulated (configure MPESA_CONSUMER_KEY for live)",
            "phone": phone,
            "amount": amount,
            "CheckoutRequestID": f"ws_CO_DEMO_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "ResponseDescription": "Success",
        }

    # Build Daraja password
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    raw = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()

    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": description,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(
                f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            data = res.json()
            data["success"] = data.get("ResponseCode") == "0"
            return data
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── X402 QR generators ──────────────────────────────────────────

def generate_x402_uri(
    recipient: str,
    amount: float,
    currency: str = "HBAR",
    memo: str = "",
    callback: str = "",
) -> str:
    """Generate an X402-formatted payment URI."""
    parts = [
        f"x402:pay",
        f"?to={recipient}",
        f"&amount={amount}",
        f"&currency={currency}",
        f"&network=hedera-testnet",
    ]
    if memo:
        parts.append(f"&memo={memo.replace(' ', '%20')}")
    if callback:
        parts.append(f"&callback={callback}")
    return "".join(parts)


def qr_data_url(uri: str) -> Optional[str]:
    """Generate QR as base64 PNG data URL using qrcode library."""
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1B4332", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except ImportError:
        # Return the URI itself as fallback — frontend can generate QR on its own
        return uri
