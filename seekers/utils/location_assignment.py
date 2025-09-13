def assign_location_fields(form):
    """
    Explicitly assign location fields from form.cleaned_data to form.instance
    for SeekerPost.
    Supports both `post_` prefixed fields (form inputs) 
    and seeker-prefixed model fields.
    """
    mapping = {
        "seeker_town": ["post_town", "post_town_input", "town", "town_input"],
        "seeker_state": ["post_state", "post_state_input", "state", "state_input"],
        "seeker_country": ["post_country", "post_country_input", "country", "country_input"],
        "seeker_continent": ["post_continent", "post_continent_input", "continent", "continent_input"],
    }

    for model_field, candidates in mapping.items():
        for field in candidates:
            if field in form.cleaned_data:
                setattr(form.instance, model_field, form.cleaned_data.get(field))
                break
