        # this code is written to double check the validity of user filled information based on the availability scope user has selected 
        # it is included in the forms.py file right 
        # 🛡️ Guard: Scope is 'town' but town is missing
def apply_location_scope_fallback(cleaned_data, form):
    scope = cleaned_data.get("availability_scope")

    fields = {
        "town": cleaned_data.get("post_town") or cleaned_data.get("post_town_input"),
        "state": cleaned_data.get("post_state") or cleaned_data.get("post_state_input"),
        "country": cleaned_data.get("post_country") or cleaned_data.get("post_country_input"),
        "continent": cleaned_data.get("post_continent") or cleaned_data.get("post_continent_input"),
    }

    if scope == "town" and not fields["town"]:
        if fields["state"]:
            cleaned_data["availability_scope"] = "state"
        elif fields["country"]:
            cleaned_data["availability_scope"] = "country"
        elif fields["continent"]:
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_town", "You selected 'Town-specific', but no location was provided.")

    elif scope == "state" and not fields["state"]:
        if fields["country"]:
            cleaned_data["availability_scope"] = "country"
        elif fields["continent"]:
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_state", "You selected 'State-wide', but no location was provided.")

    elif scope == "country" and not fields["country"]:
        if fields["continent"]:
            cleaned_data["availability_scope"] = "continent"
        else:
            form.add_error("post_country", "You selected 'Country-wide', but no location was provided.")

    elif scope == "continent" and not fields["continent"]:
        form.add_error("post_continent", "You selected 'Continent-wide', but no continent was provided.")

    return cleaned_data