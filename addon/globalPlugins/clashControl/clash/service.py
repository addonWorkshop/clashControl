from contextlib import suppress

from .client import ClashClient
from .models import ClashProxyGroup


class ClashService:
    def __init__(self, client: ClashClient, modes: list[str] | None = None):
        self.client = client
        self.data_fetched = False
        self.proxy_groups: list[ClashProxyGroup] = []
        self.modes = None if modes is None else []
        self.current_mode_index = 0

    def fetch_data(self, ignore_cache=False):
        if self.data_fetched and not ignore_cache:
            return
        proxies = self.client.get_proxies()
        self.proxy_groups.clear()
        for _proxy_name, proxy in proxies["proxies"].items():
            if proxy["type"] != "Selector":
                continue
            self.proxy_groups.append(ClashProxyGroup.from_api_object(proxy))
        configs = self.client.get_configs()
        self.modes = self.modes if self.modes is not None else configs.get("mode-list", [])
        with suppress(ValueError):
            self.current_mode_index = self.modes.index(configs["mode"])
        self.data_fetched = True

    @property
    def mode(self) -> str | None:
        return self.modes[self.current_mode_index] if self.modes else None

    def set_mode_by_index(self, mode_index: int):
        if not 0 <= mode_index < len(self.modes):
            raise ValueError("Mode not found")
        self.current_mode_index = mode_index
        self.client.patch_configs(mode=self.modes[mode_index])

    def _get_proxy(self, group_index):
        if not 0 <= group_index < len(self.proxy_groups):
            raise ValueError("Group not found")
        return self.proxy_groups[group_index]

    def select_group_proxy_by_index(self, group_index, proxy_index):
        group = self._get_proxy(group_index)
        if not 0 <= proxy_index < len(group.proxy_names):
            raise ValueError("Proxy not found")
        group.current_proxy_index = proxy_index
        return self.client.select_proxy_in_group(
            group.name,
            group.proxy_names[proxy_index],
        )
