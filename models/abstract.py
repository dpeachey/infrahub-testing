from typing import Any, Self

from pydantic import BaseModel, ConfigDict


class AbstractBaseModel(BaseModel):
    model_config = ConfigDict(
        extra_fields=False,
    )


class AbstractIpAddress(AbstractBaseModel):
    address: str


class AbstractInterface(AbstractBaseModel):
    name: str
    description: str | None
    enabled: bool
    ip_addresses: list[AbstractIpAddress]


class AbstractDevice(AbstractBaseModel):
    name: str
    description: str | None
    platform: str
    type: str
    interfaces: list[AbstractInterface]

    @classmethod
    def create(cls, infra_device: dict[str, Any]) -> Self:
        return cls(
            name=infra_device["name"]["value"],
            description=infra_device["description"]["value"],
            platform=infra_device["platform"]["node"]["name"]["value"],
            type=infra_device["type"]["value"],
            interfaces=[
                AbstractInterface(
                    name=interface["node"]["name"]["value"],
                    description=interface["node"]["description"]["value"],
                    enabled=interface["node"]["enabled"]["value"],
                    ip_addresses=[
                        AbstractIpAddress(address=ip["node"]["address"]["value"])
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
