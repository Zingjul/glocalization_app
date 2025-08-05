# Explicitly assign user location input or default to 'unspecified'
def assign_location_fields(form):
    UNSPECIFIED_ID = 1  # default fallback ID

    from custom_search.models import Continent, Country, State, Town

    # Only town has a manual input fallback
    location_mapping = {
        "post_continent": (form.cleaned_data.get("post_continent"), Continent),
        "post_country": (form.cleaned_data.get("post_country"), Country),
        "post_state": (form.cleaned_data.get("post_state"), State),
        "post_town": (
            form.cleaned_data.get("post_town") or form.cleaned_data.get("post_town_input"),
            Town,
        ),
    }

    for field, (value, model_cls) in location_mapping.items():
        if value:
            setattr(form.instance, field, value)
        else:
            try:
                fallback_obj = model_cls.objects.get(id=UNSPECIFIED_ID)
                setattr(form.instance, field, fallback_obj)
            except model_cls.DoesNotExist:
                # Optional: log or handle missing fallback
                pass

    # Clear only the input field we kept
    form.instance.post_town_input = None
