import os
import requests
import cloudscraper

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv() # <- PROVIDE YOUR OWN HEADER

def get_game_details(app_id):
    """
    Fetches and parses details (DLCs and depots for now) for a given Steam application from SteamDB.

    Args:
        app_id (str or int): Steam application ID for which details are to be fetched.

    Returns:
        dict: A dictionary with two keys:
            - 'dlc': List of dictionaries containing DLC details with keys:
                - 'dlc_id' (str): DLC AppID.
                - 'name' (str): DLC name.
            - 'depots': List of dictionaries containing depot details with keys:
                - 'depot_id' (str): DepotID.
                - 'packages' (list[str]): Package IDs associated with the depot.
                - 'details' (str): Depot details.

        Returns None if the request fails or the necessary HTML elements are not found.
    """
    url = f"https://{os.getenv('STEAMDB_HOST')}/app/{app_id}/depots/"

    ### Headers populated from .env
    headers = {
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

    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch the page for App ID {app_id}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # --- DLC Extraction ---
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
    else:
        print(f"No DLC section found for App ID {app_id}.")

    # --- Depot Extraction ---
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
    else:
        print(f"No depots section found for App ID {app_id}.")

    return {
        "dlc": dlcs,
        "depots": depots
    }

### Usage
if __name__ == "__main__":
    app_id = "appid"
    result = get_game_details(app_id)

    if result:
        print("DLC Details:")
        for dlc in result['dlc']:
            print(f"ID: {dlc['dlc_id']}, Name: {dlc['name']}")

        print("\nDepot Details:")
        for depot in result['depots']:
            print(f"Depot ID: {depot['depot_id']}, Packages: {', '.join(depot['packages'])}, Details: {depot['details']}")