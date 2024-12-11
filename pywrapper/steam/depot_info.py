import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv() # <- PROVIDE YOUR OWN HEADER

def get_depot_details(app_id):
    """
    Fetches and parses depot details for a given Steam application from SteamDB.

    Args:
        app_id (str or int): Steam application ID for which depot details are to be fetched.

    Returns:
        list[dict] or None: List of dictionaries containing depot details with the following keys:
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
        "Sec-Fetch-User": os.getenv("SEC_FETCH_USER"),
        "Priority": os.getenv("PRIORITY").strip("'")
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch the page for App ID {app_id}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the depots section in the HTML
    depots_section = soup.select_one(
        "div.container div.tabbable div.tab-content[role='tabpanel'] div.tab-pane.selected#depots"
    )
    if not depots_section:
        print(f"Depots section not found in the HTML for App ID {app_id}.")
        return None

    # Locate the depot table within the depots section
    table = depots_section.select_one(
        "table.table.table-bordered.table-hover.table-sortable.table-responsive-flex tbody"
    )
    if not table:
        print(f"Depot table not found in the HTML for App ID {app_id}.")
        return None

    # Extract depot rows from the table
    depot_rows = table.select("tr.depot")
    if not depot_rows:
        print(f"No depot rows found in the depot table for App ID {app_id}.")
        return None

    ### Parse depot details
    depots = []
    for row in depot_rows:
        depot_id = row.get("data-depotid")
        packages = row.get("data-packages", "")

        spans = row.select("td.depot-config span")
        details = " | ".join(span.get_text(separator=" ", strip=True) for span in spans)

        depots.append({
            "depot_id": depot_id,
            "packages": packages.split(",") if packages else [],
            "details": details
        })

    return depots