def assign_location_fields(form):
    """
    Explicitly assign location fields from form.cleaned_data to form.instance.
    Supports both `post_` prefixed fields (for ServicePostForm) 
    and plain fields (for PersonForm).
    """
    mapping = {
        "town": ["town", "town_input", "post_town", "post_town_input"],
        "state": ["state", "state_input", "post_state", "post_state_input"],
        "country": ["country", "country_input", "post_country", "post_country_input"],
        "continent": ["continent", "continent_input", "post_continent", "post_continent_input"],
    }

    for model_field, candidates in mapping.items():
        for field in candidates:
            if field in form.cleaned_data:
                setattr(form.instance, model_field, form.cleaned_data.get(field))
                break
