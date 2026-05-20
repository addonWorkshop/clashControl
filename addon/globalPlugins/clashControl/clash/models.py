from dataclasses import dataclass


@dataclass
class ClashProxyGroup:
    name: str
    proxy_names: list[str]
    current_proxy_index: int

    @classmethod
    def from_api_object(cls, proxy: dict) -> "ClashProxyGroup":
        proxy_names = proxy["all"]
        current_proxy_index = proxy_names.index(proxy["now"])
        return cls(
            name=proxy["name"],
            proxy_names=proxy_names,
            current_proxy_index=current_proxy_index,
        )
