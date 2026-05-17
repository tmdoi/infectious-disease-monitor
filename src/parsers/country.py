"""Country name → ISO 3166-1 alpha-3 conversion."""

import pycountry


def name_to_iso3(name: str) -> str | None:
    """Convert country name to ISO3 code. Returns None if not found."""
    result = pycountry.countries.get(name=name)
    if result:
        return result.alpha_3
    try:
        results = pycountry.countries.search_fuzzy(name)
        return results[0].alpha_3 if results else None
    except LookupError:
        return None
