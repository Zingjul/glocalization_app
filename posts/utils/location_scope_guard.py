def apply_location_scope_fallback(cleaned_data, form):
    scope = cleaned_data.get("availability_scope")
    UNSPECIFIED_ID = 1

    # Determine actual resolved objects or strings (dropdown or input only for town)
    fields = {
        "town": cleaned_data.get("post_town") or cleaned_data.get("post_town_input"),
        "state": cleaned_data.get("post_state"),
        "country": cleaned_data.get("post_country"),
        "continent": cleaned_data.get("post_continent"),
    }

    # Check if field is unspecified or fallback object
    def is_unspecified(value):
        if hasattr(value, "id"):
            return value.id == UNSPECIFIED_ID
        return not value or str(value).strip().lower() in ["", "unspecified"]

    # Apply fallback logic
    if scope == "town" and is_unspecified(fields["town"]):
        if not is_unspecified(fields["state"]):
            cleaned_data["availability_scope"] = "state"
        elif not is_unspecified(fields["country"]):
            cleaned_data["availability_scope"] = "country"
        elif not is_unspecified(fields["continent"]):
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_town", "You selected 'Town-specific', but no valid town was provided.")

    elif scope == "state" and is_unspecified(fields["state"]):
        if not is_unspecified(fields["country"]):
            cleaned_data["availability_scope"] = "country"
        elif not is_unspecified(fields["continent"]):
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_state", "You selected 'State-wide', but no valid state was provided.")

    elif scope == "country" and is_unspecified(fields["country"]):
        if not is_unspecified(fields["continent"]):
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_country", "You selected 'Country-wide', but no valid country was provided.")

    elif scope == "continent" and is_unspecified(fields["continent"]):
        form.add_error("post_continent", "You selected 'Continent-wide', but no valid continent was provided.")

    return cleaned_data