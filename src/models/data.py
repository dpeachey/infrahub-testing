from typing import Any, Self

from models.base import BaseDataModel


class IpAddressData(BaseDataModel):
    address: str


class InterfaceData(BaseDataModel):
    name: str
    description: str | None
    enabled: bool
    ip_addresses: list[IpAddressData]


class DeviceData(BaseDataModel):
    name: str
    description: str | None
    platform: str
    type: str
    interfaces: list[InterfaceData]

    @classmethod
    def create(cls, infra_device: dict[str, Any]) -> Self:
        return cls(
            name=infra_device["name"]["value"],
            description=infra_device["description"]["value"],
            platform=infra_device["platform"]["node"]["name"]["value"],
            type=infra_device["type"]["value"],
            interfaces=[
                InterfaceData(
                    name=interface["node"]["name"]["value"],
                    description=interface["node"]["description"]["value"],
                    enabled=interface["node"]["enabled"]["value"],
                    ip_addresses=[
                        IpAddressData(address=ip["node"]["address"]["value"])
                        for ip in interface["node"]["ip_addresses"]["edges"]
                    ]
                    if interface["node"].get("ip_addresses")
                    else [],
                )
                for interface in infra_device["interfaces"]["edges"]
            ]
            if infra_device.get("interfaces")
            else [],
        )
