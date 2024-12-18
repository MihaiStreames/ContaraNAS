import os
import requests
import cloudscraper

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv() # <- SUPPLY YOUR OWN


class SteamDBScraper:
    def __init__(self):
        self.base_url = f"https://{os.getenv('STEAMDB_HOST')}"
        self.headers = {
            "Host": os.getenv("STEAMDB_HOST"),
            "User-Agent": os.getenv("USER_AGENT").strip("'"),
            "Accept": os.getenv("ACCEPT"),
            "Accept-Language": os.getenv("ACCEPT_LANGUAGE"),
            "Accept-Encoding": os.getenv("ACCEPT_ENCODING").strip("'"),
            "Referer": os.getenv("REFERER"),
            "DNT": os.getenv("DNT"),
            "Sec-GPC": os.getenv("SEC_GPC"),
            "Cookie": os.getenv("COOKIE"),
            "Upgrade-Insecure-Requests": os.getenv("UPGRADE_INSECURE_REQUESTS"),
            "Sec-Fetch-Dest": os.getenv("SEC_FETCH_DEST"),
            "Sec-Fetch-Mode": os.getenv("SEC_FETCH_MODE"),
            "Sec-Fetch-Site": os.getenv("SEC_FETCH_SITE"),
            "Priority": os.getenv("PRIORITY").strip("'")
        }

        self.scraper = cloudscraper.create_scraper()

    def get_game_details(self, app_id):
        url = f"{self.base_url}/app/{app_id}/depots/"

        try:
            response = self.scraper.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Failed to fetch the page for App ID {app_id}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        dlcs = self._extract_dlcs(soup)
        depots = self._extract_depots(soup)

        return {"dlc": dlcs, "depots": depots}

    def _extract_dlcs(self, soup):
        dlc_section = soup.select_one("div#dlc")
        dlcs = []

        if dlc_section:
            tbody = dlc_section.select_one("tbody")

            if tbody:
                for row in tbody.select("tr.app"):
                    dlc_id = row.get("data-appid")
                    name_cell = row.select_one("td:nth-of-type(2)")
                    name = name_cell.get_text(strip=True) if name_cell else "Unknown DLC"

                    if dlc_id:
                        dlcs.append({"dlc_id": dlc_id, "name": name})

        return dlcs

    def _extract_depots(self, soup):
        depots_section = soup.select_one("div#depots")
        depots = []

        if depots_section:
            table = depots_section.select_one("tbody")

            if table:
                for row in table.select("tr.depot"):
                    depot_id = row.get("data-depotid")
                    packages = row.get("data-packages", "")
                    spans = row.select("td.depot-config span")
                    details = " | ".join(span.get_text(separator=" ", strip=True) for span in spans)

                    if depot_id:
                        depots.append({
                            "depot_id": depot_id,
                            "packages": packages.split(",") if packages else [],
                            "details": details
                        })

        return depots