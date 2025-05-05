import pycountry
import json

def get_all_states_with_country_data():
    """
    Retrieves a dictionary where keys are country names and values are lists of
    dictionaries, each containing state/province/region name, ID, and country.

    Returns:
        dict: A dictionary of country names and their corresponding state information.
              Each state is represented as a dictionary with 'name', 'id', and 'country' keys.
              Returns an empty dict if no states are found for a country.
    """
    country_states = {}

    for country in pycountry.countries:
        subdivisions = pycountry.subdivisions.get(country_code=country.alpha_2)
        
        if subdivisions:
            state_data = [{
                'name': subdivision.name,
                'id': subdivision.code,
                'country': country.name  # Add the country name
            } for subdivision in subdivisions]
            country_states[country.name] = state_data
        else:
            country_states[country.name] = []
            
    return country_states

def save_to_json(data, filename="country_states.json"):
    """
    Saves the given data to a JSON file.

    Args:
        data (dict): The data to be saved as JSON.
        filename (str, optional): The name of the file to save to.
            Defaults to "country_states.json".
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

def main():
    """
    Main function to execute the script.
    """
    all_states_data = get_all_states_with_country_data()
    save_to_json(all_states_data)

if __name__ == "__main__":
    main()
