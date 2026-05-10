from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
import io

def preprocess_image(image_bytes: bytes) -> bytes:
    """Sharpen, denoise, crop borders, boost contrast — return processed bytes."""
    # Load with OpenCV for denoising
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_cv is None:
        raise ValueError("Could not decode image bytes")

    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)
    
    # Convert back to PIL
    img_pil = Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))

    # Sharpen
    img_pil = img_pil.filter(ImageFilter.SHARPEN)

    # Boost contrast
    enhancer = ImageEnhance.Contrast(img_pil)
    img_pil = enhancer.enhance(1.5)

    # Convert to grayscale for better OCR
    img_pil = img_pil.convert('L')

    # Auto-crop white borders (if any)
    # Note: getbbox returns (left, top, right, bottom)
    bbox = img_pil.getbbox()
    if bbox:
        img_pil = img_pil.crop(bbox)

    out = io.BytesIO()
    img_pil.save(out, format='JPEG', quality=95)
    return out.getvalue()
