from django.http import JsonResponse
# ✅ universal phone code source (ISO2 → phone prefix)
PHONE_CODES = {
    "NG": "+234", "GH": "+233", "US": "+1", "CA": "+1", "GB": "+44", "FR": "+33", "DE": "+49", "ZA": "+27",
    "IN": "+91", "CN": "+86", "JP": "+81", "BR": "+55", "RU": "+7", "EG": "+20", "KE": "+254", "TZ": "+255",
    "UG": "+256", "ET": "+251", "SD": "+249", "SA": "+966", "AE": "+971", "TR": "+90", "PK": "+92", "ID": "+62",
    "MX": "+52", "AR": "+54", "AU": "+61", "NZ": "+64", "IT": "+39", "ES": "+34", "NL": "+31", "SE": "+46",
    "NO": "+47", "FI": "+358", "PL": "+48", "BE": "+32", "CH": "+41", "AT": "+43", "IR": "+98", "IQ": "+964",
    "SY": "+963", "YE": "+967", "MA": "+212", "DZ": "+213", "TN": "+216", "LY": "+218", "CM": "+237", "SN": "+221",
    "GH": "+233", "CI": "+225", "ML": "+223", "NE": "+227", "BF": "+226", "ZM": "+260", "ZW": "+263",
    "MW": "+265", "MZ": "+258", "BW": "+267", "NA": "+264", "LS": "+266", "SZ": "+268", "RW": "+250",
    "AF": "+93", "AL": "+355", "AM": "+374", "AZ": "+994", "BD": "+880", "BG": "+359", "BO": "+591", "CL": "+56", "CO": "+57",     "CR": "+506", "CZ": "+420",
    "DK": "+45", "DO": "+1", "EC": "+593", "GR": "+30", "GT": "+502", "HN": "+504", "HU": "+36",  "IE": "+353", "IL": "+972", "JM": "+1",      "JO": "+962",    "KR": "+82",  
    "KZ": "+7", "LB": "+961", "LK": "+94", "LT": "+370", "LU": "+352", "LV": "+371", "MD": "+373", "MN": "+976", "MY": "+60",     "NG": "+234", "PA": "+507",    "PE": "+51",     "PH": "+63",     "PT": "+351",    "RO": "+40",     "RS": "+381",    "SG": "+65",     "SK": "+421",    "SL": "+232",
    "TH": "+66", "UA": "+380", "UY": "+598", "VE": "+58", "VN": "+84",     # You can keep extending this — or use pycountry + phonenumbers for full coverage later
} 

def get_phone_code(request):
    """
    Return the phone code based on the country's ISO2 code
    stored in Country.country_code (django_countries field).
    """
    iso2 = request.GET.get("country_code", "").upper().strip()
    phone_code = ""

    if iso2:
        country = Country.objects.filter(country_code=iso2).first()
        if country:
            # Prefer stored value
            phone_code = country.phone_code or PHONE_CODES.get(iso2, "")
            # Auto-fill DB if missing
            if not country.phone_code and phone_code:
                country.phone_code = phone_code
                country.save(update_fields=["phone_code"])
        else:
            phone_code = PHONE_CODES.get(iso2, "")

    return JsonResponse({"phone_code": phone_code})

def get_phone_code_by_iso2(iso2):
    """
    Return the phone code string for a given ISO2 country code.
    Checks the Country model first, then falls back to PHONE_CODES dict.
    """
    iso2 = str(iso2).upper().strip()
    phone_code = ""
    if iso2:
        from custom_search.models import Country  # Import here to avoid circular import
        country = Country.objects.filter(country_code=iso2).first()
        if country:
            phone_code = country.phone_code or PHONE_CODES.get(iso2, "")
            if not country.phone_code and phone_code:
                country.phone_code = phone_code
                country.save(update_fields=["phone_code"])
        else:
            phone_code = PHONE_CODES.get(iso2, "")
    return phone_code

def get_phone_code_api(request):
    """
    API endpoint: Return the phone code for a given country_code in GET params.
    """
    iso2 = request.GET.get("country_code", "")
    phone_code = get_phone_code_by_iso2(iso2)
    return JsonResponse({"phone_code": phone_code})