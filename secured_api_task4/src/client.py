import time
import requests

def fetch_all(url, client_id="demo-client", client_secret="demo-secret",
              token_url=None, session=None, sleep_fn=time.sleep):
    """Fetch offset-paginated JSON items; refresh bearer token on 401."""
    http = session or requests.Session()
    token_url = token_url or url.rsplit("/", 1)[0] + "/oauth/token"
    token = None
    page = 1
    all_items = []
    while True:
        if token is None:
            token_response = http.post(token_url, json={
                "client_id": client_id, "client_secret": client_secret
            })
            token_response.raise_for_status()
            token = token_response.json()["access_token"]

        response = http.get(url, params={"page": page, "per_page": 100},
                            headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 401:
            token = None
            continue
        response.raise_for_status()
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            retry_after = float(response.headers.get("Retry-After", "1"))
            sleep_fn(retry_after)
        items = response.json()
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items
