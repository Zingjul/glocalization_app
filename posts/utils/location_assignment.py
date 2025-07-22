# we want to manually(explicitely) assign user input of location this is to make sure the locations aint left out
def assign_location_fields(form):
    location_fields = [
        "post_town", "post_town_input",
        "post_state", "post_state_input",
        "post_country", "post_country_input",
        "post_continent", "post_continent_input",
    ]
    for field in location_fields:
        setattr(form.instance, field, form.cleaned_data.get(field))
