# media_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import MediaFile
from .forms import MediaFileForm
from PIL import Image, UnidentifiedImageError
import magic
import clamd
import os
import re

# Helper for additional runtime validation
def secure_file_check(uploaded_file, file_type):
    # 1️⃣ Confirm MIME type again
    mime = magic.from_buffer(uploaded_file.read(4096), mime=True)
    uploaded_file.seek(0)
    
    if file_type == "image" and mime not in ["image/jpeg", "image/png", "image/webp"]:
        raise ValidationError("Invalid image format detected at runtime.")
    if file_type == "video" and mime not in ["video/mp4", "video/webm", "video/ogg"]:
        raise ValidationError("Invalid video format detected at runtime.")

    # 2️⃣ Confirm extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    valid_exts = [".jpg", ".jpeg", ".png", ".webp"] if file_type == "image" else [".mp4", ".webm", ".ogg"]
    if ext not in valid_exts:
        raise ValidationError("File extension mismatch at runtime.")

    # 3️⃣ Antivirus scan (ClamAV)
    try:
        cd = clamd.ClamdNetworkSocket(host="127.0.0.1", port=3310)
        result = cd.instream(uploaded_file)
        uploaded_file.seek(0)
        if result and "FOUND" in result.get("stream", [""])[1]:
            raise ValidationError("Malware detected in uploaded file.")
    except Exception:
        print("⚠️ ClamAV not running — skipping antivirus scan.")

    # 4️⃣ Additional image checks
    if file_type == "image":
        try:
            img = Image.open(uploaded_file)
            img.verify()  # Ensure it's not corrupted
            uploaded_file.seek(0)
        except UnidentifiedImageError:
            raise ValidationError("Uploaded image is invalid.")
        except Exception:
            raise ValidationError("Failed to verify uploaded image.")

@login_required
def upload_media(request):
    if request.method == "POST":
        files = request.FILES.getlist("media_files[]")
        if not files:
            messages.error(request, "No files selected.")
            return render(request, "media_app/upload.html", {"form": MediaFileForm()})

        for f in files:
            file_type = "video" if f.content_type.startswith("video") else "image"
            try:
                secure_file_check(f, file_type)
                media = MediaFile(owner=request.user, file=f, file_type=file_type)
                media.save()
            except ValidationError as e:
                messages.error(request, f"Upload failed for {f.name}: {e}")
                continue  # Skip bad files but keep processing others

        messages.success(request, "Media upload complete!")
        return redirect("media_list")

    return render(request, "media_app/upload.html", {"form": MediaFileForm()})

@login_required
def media_list(request):
    # Only allow user to see their own files
    files = MediaFile.objects.filter(owner=request.user)
    return render(request, "media_app/list.html", {"files": files})

@login_required
def delete_media(request, pk):
    # Ensure user owns the file
    media = get_object_or_404(MediaFile, pk=pk, owner=request.user)
    if request.method == "POST":
        media.delete()
        messages.success(request, "Media deleted successfully!")
        return redirect("media_list")
    return render(request, "media_app/confirm_delete.html", {"media": media})
