import httpx

from app.config import get_settings
from app.services.cache import cache


async def reverse_geocode(latitude: float, longitude: float) -> str | None:
    cache_key = f"reverse:{latitude:.5f}:{longitude:.5f}"
    cached = cache.get_json(cache_key)
    if cached:
        return str(cached)

    settings = get_settings()
    address = await _google_reverse_geocode(latitude, longitude) if settings.google_maps_api_key else None
    if address is None:
        address = await _openstreetmap_reverse_geocode(latitude, longitude)
    if address:
        cache.set_json(cache_key, address, ttl_seconds=60 * 60 * 24)
    return address


async def _google_reverse_geocode(latitude: float, longitude: float) -> str | None:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{latitude},{longitude}", "key": settings.google_maps_api_key},
        )
    if response.status_code != 200:
        return None
    results = response.json().get("results") or []
    return results[0].get("formatted_address") if results else None


async def _openstreetmap_reverse_geocode(latitude: float, longitude: float) -> str | None:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=8, headers={"User-Agent": settings.nominatim_user_agent}) as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": latitude, "lon": longitude},
        )
    if response.status_code != 200:
        return None
    return response.json().get("display_name")
