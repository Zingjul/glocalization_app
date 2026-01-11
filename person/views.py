import logging
from django.contrib.contenttypes.models import ContentType
from media_app.models import MediaFile
from media_app.utils import validate_video_duration, format_duration
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from accounts.models import Follow
from .forms import PersonForm, GalleryUploadForm, MultipleGalleryUploadForm
from .models import Person, PendingLocationRequest
from accounts.models import CustomUser
from custom_search.models import Continent, Country, State, Town

logger = logging.getLogger(__name__)


class PersonSetupView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Create or update the logged-in user's Person profile."""

    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def get_object(self, queryset=None):
        """Always return the logged-in user's profile."""
        return self.request.user.profile

    def get_success_url(self):
        """Redirect to profile detail after setup/update."""
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        """Only allow the owner to edit, and not while pending."""
        person = self.get_object()
        return person.user == self.request.user and person.approval_status != "pending"

    def handle_no_permission(self):
        messages.warning(
            self.request,
            "Your profile is under review and cannot be edited until approved."
        )
        return redirect("person_detail", pk=self.get_object().pk)

    def form_valid(self, form):
        """Handle town logic and pending approvals."""
        from custom_search.models import Town

        person = form.save(commit=False)
        person.user = self.request.user

        selected_town_id = self.request.POST.get("town")
        typed_town_name = self.request.POST.get("town_input", "").strip()

        # Ensure fallback "Unspecified" town exists
        unspecified_town = Town.objects.filter(id=0).first()
        if not unspecified_town:
            form.add_error("town", "System error: Unspecified town not found.")
            return self.form_invalid(form)

        if selected_town_id and selected_town_id != "0":
            try:
                person.town = Town.objects.get(id=selected_town_id)
            except Town.DoesNotExist:
                form.add_error("town", "Selected town does not exist.")
                return self.form_invalid(form)

        elif typed_town_name:
            # Fallback assignment for typed towns
            person.town = unspecified_town
            person.approval_status = "pending"
            person.save()

            PendingLocationRequest.objects.update_or_create(
                person=person,
                defaults={
                    "typed_town": typed_town_name,
                    "parent_state": form.cleaned_data.get("state"),
                    "is_reviewed": False,
                    "approved": False,
                },
            )

            messages.success(
                self.request,
                "Profile updated successfully! Your town is pending admin approval."
            )
            return super().form_valid(form)
        person.approval_status = "pending"
        person.save()
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add location dropdowns and profile status to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            "continents": Continent.objects.all(),
            "countries": Country.objects.all(),
            "states": State.objects.all(),
            "towns": Town.objects.all(),
            "location_fields": ["continent", "country", "state", "town"],
            "location_input_fields": ["continent_input", "country_input", "state_input", "town_input"],
            "has_pending_location": hasattr(self.object, "pending_location_request"),
            "approval_status": self.object.approval_status,
        })
        return context


class PersonListView(LoginRequiredMixin, ListView):
    """List all registered and approved Person profiles."""

    model = Person
    template_name = "person/person_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        # Only return profiles with approval_status = "approved"
        qs = Person.objects.filter(
            approval_status="approved"
        ).exclude(user=self.request.user)
        logger.debug("Retrieved %s approved profiles (excluding current user)", qs.count())
        return qs


class PersonDetailView(LoginRequiredMixin, DetailView):
    """Display details of a Person profile."""
    model = Person
    template_name = "person/person_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        context["profile"] = profile

        # Check if current logged-in user already follows this profile.user
        is_followed = Follow.objects.filter(
            follower=self.request.user,
            following=profile.user
        ).exists()

        context["is_followed"] = is_followed
        return context


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a user account (CustomUser + Person).""" 
    model = CustomUser
    template_name = "person/person_confirm_delete.html"
    success_url = reverse_lazy("post_home")

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        logger.warning("Deleting user %s and logging them out", user.pk)
        logout(request)
        messages.success(request, "Your account has been deleted. Goodbye!")
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_business_name(request):
    """Toggle whether to display the business name instead of personal name."""
    try:
        profile = request.user.profile
    except Person.DoesNotExist:
        messages.error(request, "Profile not found. Please create one first.")
        return redirect("person_create")

    profile.use_business_name = not profile.use_business_name
    profile.save()
    state = "now visible" if profile.use_business_name else "hidden"
    messages.success(request, f"Business name is {state} on your profile.")
    logger.info("User %s toggled business name visibility to %s", request.user.pk, state)
    return redirect("person_detail", pk=profile.pk)


# ============================================
# GALLERY VIEWS
# ============================================

# Upload limits
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB for images
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB fallback for videos (duration is primary limit)
MAX_VIDEO_DURATION = 90  # 1 minute 30 seconds
MAX_GALLERY_ITEMS = 50


@login_required
def gallery_view(request):
    """Display user's gallery with upload form."""
    try:
        person = request.user.profile
    except Person.DoesNotExist:
        messages.error(request, "Profile not found. Please create one first.")
        return redirect("person_create")
    
    gallery_items = person.media_files.all()
    form = MultipleGalleryUploadForm()
    
    context = {
        'person': person,
        'gallery_items': gallery_items,
        'form': form,
        'image_count': gallery_items.filter(file_type='image').count(),
        'video_count': gallery_items.filter(file_type='video').count(),
    }
    logger.debug("User %s viewing gallery with %s items", request.user.pk, gallery_items.count())
    return render(request, 'person/gallery.html', context)


@login_required
def gallery_upload(request):
    """Handle multiple file uploads to gallery using MediaFile."""
    if request.method != 'POST':
        return redirect('gallery_view')
    
    try:
        person = request.user.profile
    except Person.DoesNotExist:
        messages.error(request, "Profile not found. Please create one first.")
        return redirect("person_create")
    
    files = request.FILES.getlist('files')
    
    if not files:
        messages.warning(request, "No files selected for upload.")
        return redirect('gallery_view')
    
    # Check gallery limit
    current_count = person.media_files.count()
    
    if current_count + len(files) > MAX_GALLERY_ITEMS:
        remaining = MAX_GALLERY_ITEMS - current_count
        messages.error(
            request, 
            f"Gallery limit exceeded. You can upload {remaining} more item(s)."
        )
        return redirect('gallery_view')
    
    # Get ContentType for Person model
    person_content_type = ContentType.objects.get_for_model(Person)
    
    uploaded_count = 0
    failed_count = 0
    failed_reasons = []
    
    # Allowed extensions
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
    video_extensions = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']
    allowed_extensions = image_extensions + video_extensions
    
    for file in files:
        try:
            extension = file.name.lower().split('.')[-1]
            
            # Validate file extension
            if extension not in allowed_extensions:
                failed_count += 1
                failed_reasons.append(f"{file.name}: Invalid file type")
                logger.warning("File %s has invalid extension for user %s", file.name, request.user.pk)
                continue
            
            # Determine file type and validate
            if extension in video_extensions:
                file_type = 'video'
                
                # Check video file size (as backup limit)
                if file.size > MAX_VIDEO_SIZE:
                    failed_count += 1
                    size_mb = MAX_VIDEO_SIZE // (1024 * 1024)
                    failed_reasons.append(f"{file.name}: Exceeds {size_mb}MB limit")
                    logger.warning("Video %s exceeds size limit for user %s", file.name, request.user.pk)
                    continue
                
                # Validate video duration (primary limit)
                is_valid, duration, error_msg = validate_video_duration(file, MAX_VIDEO_DURATION)
                
                if not is_valid:
                    failed_count += 1
                    if duration:
                        duration_str = format_duration(duration)
                        max_duration_str = format_duration(MAX_VIDEO_DURATION)
                        failed_reasons.append(f"{file.name}: Too long ({duration_str}, max {max_duration_str})")
                    else:
                        failed_reasons.append(f"{file.name}: {error_msg}")
                    logger.warning(
                        "Video %s exceeds duration limit (%.1fs) for user %s", 
                        file.name, duration or 0, request.user.pk
                    )
                    continue
                    
            else:
                file_type = 'image'
                
                # Check image file size
                if file.size > MAX_IMAGE_SIZE:
                    failed_count += 1
                    size_mb = MAX_IMAGE_SIZE // (1024 * 1024)
                    failed_reasons.append(f"{file.name}: Exceeds {size_mb}MB limit")
                    logger.warning("Image %s exceeds size limit for user %s", file.name, request.user.pk)
                    continue
            
            # Create MediaFile with generic relation to Person
            MediaFile.objects.create(
                owner=request.user,
                content_type=person_content_type,
                object_id=person.pk,
                file=file,
                file_type=file_type,
                is_public=True
            )
            uploaded_count += 1
            
        except Exception as e:
            failed_count += 1
            failed_reasons.append(f"{file.name}: Upload error")
            logger.error("Error uploading file %s for user %s: %s", file.name, request.user.pk, str(e))
    
    # Success message
    if uploaded_count > 0:
        messages.success(request, f'{uploaded_count} file(s) uploaded successfully!')
    
    # Failure messages with details
    if failed_count > 0:
        if len(failed_reasons) <= 3:
            reason_text = " | ".join(failed_reasons)
            messages.warning(request, f'{failed_count} file(s) failed: {reason_text}')
        else:
            # Show first 3 reasons + count of others
            shown_reasons = " | ".join(failed_reasons[:3])
            remaining = failed_count - 3
            messages.warning(request, f'{failed_count} file(s) failed: {shown_reasons} (+{remaining} more)')
    
    logger.info("User %s uploaded %s files, %s failed", request.user.pk, uploaded_count, failed_count)
    return redirect('gallery_view')


@login_required
def gallery_delete(request, pk):
    """Delete a gallery item (MediaFile)."""
    item = get_object_or_404(MediaFile, pk=pk)
    
    # Ensure user owns this media file
    if item.owner != request.user:
        messages.error(request, "You don't have permission to delete this item.")
        logger.warning("User %s attempted to delete media %s owned by another user", request.user.pk, pk)
        return redirect('gallery_view')
    
    if request.method == 'POST':
        try:
            # Delete the actual file from storage
            if item.file:
                item.file.delete(save=False)
            item.delete()
            messages.success(request, 'Gallery item deleted successfully!')
            logger.info("User %s deleted media item %s", request.user.pk, pk)
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
        except Exception as e:
            messages.error(request, 'Error deleting item. Please try again.')
            logger.error("Error deleting media item %s for user %s: %s", pk, request.user.pk, str(e))
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return redirect('gallery_view')


@login_required
def gallery_update_caption(request, pk):
    """Update caption for a gallery item (MediaFile)."""
    item = get_object_or_404(MediaFile, pk=pk)
    
    # Ensure user owns this media file
    if item.owner != request.user:
        messages.error(request, "You don't have permission to edit this item.")
        return redirect('gallery_view')
    
    if request.method == 'POST':
        caption = request.POST.get('caption', '').strip()
        item.caption = caption
        item.save()
        messages.success(request, 'Caption updated successfully!')
        logger.info("User %s updated caption for media item %s", request.user.pk, pk)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'caption': caption})
    
    return redirect('gallery_view')


@login_required
def gallery_toggle_visibility(request, pk):
    """Toggle public/private visibility of a gallery item."""
    item = get_object_or_404(MediaFile, pk=pk)
    
    if item.owner != request.user:
        messages.error(request, "You don't have permission to modify this item.")
        return redirect('gallery_view')
    
    if request.method == 'POST':
        item.is_public = not item.is_public
        item.save()
        status = "public" if item.is_public else "private"
        messages.success(request, f'Item is now {status}.')
        logger.info("User %s toggled visibility for media item %s to %s", request.user.pk, pk, status)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'is_public': item.is_public})
    
    return redirect('gallery_view')