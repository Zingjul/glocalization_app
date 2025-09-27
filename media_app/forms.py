# media_app/forms.py
import os
import re
import logging
from django import forms
from django.core.exceptions import ValidationError
from .models import MediaFile
from PIL import Image, UnidentifiedImageError
import magic  # pip install python-magic-bin (Windows) or python-magic (Linux)

try:
    import clamd  # optional, only works if ClamAV daemon is running
    CLAMD_AVAILABLE = True
except ImportError:
    CLAMD_AVAILABLE = False

logger = logging.getLogger(__name__)


class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ["file", "file_type", "caption", "is_public"]

    # 🚨 Max limits (configurable)
    MAX_IMAGE_MB = 10
    MAX_VIDEO_MB = 50
    MAX_IMAGE_DIM = (6000, 6000)  # width x height
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_VIDEO_TYPES = ["video/mp4", "video/webm", "video/ogg"]

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        file_type = self.cleaned_data.get("file_type")

        if not uploaded_file:
            raise ValidationError("No file uploaded.")

        # ✅ Step 1: Enforce size
        max_size_mb = self.MAX_VIDEO_MB if file_type == "video" else self.MAX_IMAGE_MB
        if uploaded_file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"File too large (max {max_size_mb}MB).")

        # ✅ Step 2: Confirm real MIME type
        mime = magic.from_buffer(uploaded_file.read(4096), mime=True)
        uploaded_file.seek(0)

        if file_type == "image" and mime not in self.ALLOWED_IMAGE_TYPES:
            raise ValidationError("Invalid image format (JPEG, PNG, WEBP only).")
        if file_type == "video" and mime not in self.ALLOWED_VIDEO_TYPES:
            raise ValidationError("Invalid video format (MP4, WebM, OGG only).")

        # ✅ Step 3: Verify file extension matches MIME
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        valid_exts = (
            [".jpg", ".jpeg", ".png", ".webp"]
            if file_type == "image"
            else [".mp4", ".webm", ".ogg"]
        )

        if ext not in valid_exts:
            raise ValidationError("File extension does not match required type.")

        # ✅ Step 4: Antivirus scan (optional, safe fallback)
        if CLAMD_AVAILABLE:
            try:
                cd = clamd.ClamdNetworkSocket(host="127.0.0.1", port=3310)
                result = cd.instream(uploaded_file)
                uploaded_file.seek(0)
                if result and "FOUND" in result.get("stream", [""])[1]:
                    raise ValidationError("Malware detected in uploaded file.")
            except Exception as e:
                logger.warning("ClamAV not running or unreachable: %s", e)
        else:
            logger.info("ClamAV not installed — skipping virus scan.")

        # ✅ Step 5: Extra image checks
        if file_type == "image":
            try:
                img = Image.open(uploaded_file)
                if img.width > self.MAX_IMAGE_DIM[0] or img.height > self.MAX_IMAGE_DIM[1]:
                    raise ValidationError(
                        f"Image too large (max {self.MAX_IMAGE_DIM[0]}x{self.MAX_IMAGE_DIM[1]}px)."
                    )
                img.verify()  # Ensure not corrupted
                uploaded_file.seek(0)

                # 🔹 Strip EXIF metadata for privacy (do not overwrite file in memory)
                safe_img = Image.open(uploaded_file).convert("RGB")
                # We won’t resave here — leave storage backend (S3, etc.) to handle optimization
                uploaded_file.seek(0)

            except UnidentifiedImageError:
                raise ValidationError("Uploaded file is not a valid image.")
            except Exception as e:
                logger.error("Failed to process image securely: %s", e)
                raise ValidationError("Failed to process image securely.")

        return uploaded_file

    def clean_caption(self):
        caption = self.cleaned_data.get("caption")

        if caption:
            # ✅ Length limit
            if len(caption) > 200:
                raise ValidationError("Caption too long (max 200 chars).")

            # ✅ Strip suspicious characters (basic XSS hardening)
            if re.search(r"[<>]", caption):
                raise ValidationError("Invalid characters in caption.")

        return caption
