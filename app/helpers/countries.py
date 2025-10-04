from countryinfo import CountryInfo


def get_country_states_dict():
    """
    Returns a dictionary mapping countries to their states/provinces.
    """
    country = CountryInfo()
    countries = country.all()

    country_state_map = {
        info['name']: info['provinces'] for _, info in countries.items()}

    return country_state_map
