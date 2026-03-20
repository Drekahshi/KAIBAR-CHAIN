import qrcode
import os

qr_dir = "storage/qrcodes"
os.makedirs(qr_dir, exist_ok=True)

def generate_qr(address, amount):
    """
    Generates a QR code for a Hedera payment.
    """
    data = f"hedera:{address}?amount={amount}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"{qr_dir}/payment_{address[:8]}.png"
    img.save(filename)
    print(f"QR Code generated and saved to {filename}")
    return filename
