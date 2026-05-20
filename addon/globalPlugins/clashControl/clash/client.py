import requests


class ClashClient:
    def __init__(self, *, clash_base_url: str, clash_secret: str):
        self.clash_base_url = clash_base_url
        self.client = requests.Session()
        self.client.headers["Authorization"] = f"Bearer {clash_secret}"

    def send_request(self, method: str, path: str, *, return_json=True, **kwargs):
        url = f"{self.clash_base_url}/{path}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if return_json else response

    def get_configs(self):
        return self.send_request("GET", "configs")

    def patch_configs(self, mode: str | None = None):
        patch = {
            **({} if mode is None else {"mode": mode}),
        }
        return self.send_request("PATCH", "configs", json=patch, return_json=False)

    def get_proxies(self):
        return self.send_request("GET", "proxies")

    def select_proxy_in_group(self, proxy_group_name: str, proxy_name: str):
        return self.send_request(
            "PUT",
            f"proxies/{proxy_group_name}",
            json={"name": proxy_name},
            return_json=False,
        )
