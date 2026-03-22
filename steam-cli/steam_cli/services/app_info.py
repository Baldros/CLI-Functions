from __future__ import annotations

from steam_cli.providers.steam_storefront import SteamStorefrontProvider


class AppInfoService:
    def __init__(self, provider: SteamStorefrontProvider | None = None) -> None:
        self.provider = provider or SteamStorefrontProvider()

    def get_details(self, appid: int, *, cc: str = "br", lang: str = "portuguese") -> dict:
        data = self.provider.get_app_details(appid, cc=cc, lang=lang)
        return self._summarize(data)

    @staticmethod
    def _summarize(data: dict) -> dict:
        genres = [genre.get("description") for genre in data.get("genres", []) if isinstance(genre, dict)]
        categories = [cat.get("description") for cat in data.get("categories", []) if isinstance(cat, dict)]

        price = data.get("price_overview") or {}
        release = data.get("release_date") or {}
        metacritic = data.get("metacritic") or {}
        recommendations = data.get("recommendations") or {}

        return {
            "steam_appid": data.get("steam_appid"),
            "name": data.get("name"),
            "type": data.get("type"),
            "is_free": data.get("is_free"),
            "required_age": data.get("required_age"),
            "developers": data.get("developers") or [],
            "publishers": data.get("publishers") or [],
            "genres": genres,
            "categories": categories,
            "release_date": release.get("date"),
            "coming_soon": release.get("coming_soon"),
            "short_description": data.get("short_description"),
            "supported_languages": data.get("supported_languages"),
            "platforms": data.get("platforms") or {},
            "price_overview": {
                "currency": price.get("currency"),
                "initial": price.get("initial"),
                "final": price.get("final"),
                "discount_percent": price.get("discount_percent"),
                "initial_formatted": price.get("initial_formatted"),
                "final_formatted": price.get("final_formatted"),
            },
            "metacritic": {
                "score": metacritic.get("score"),
                "url": metacritic.get("url"),
            },
            "recommendations_total": recommendations.get("total"),
            "header_image": data.get("header_image"),
            "website": data.get("website"),
        }
