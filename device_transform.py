import sys

sys.path.append(".")
from typing import Any

from config_gen.device import Device
from infrahub_sdk.transforms import InfrahubTransform
from models.abstract import AbstractDevice, AbstractInterface, AbstractIpAddress


class DeviceTransformJson(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-json"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = get_device(data)
        return device.json_config


class DeviceTransformCli(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-cli"

    async def transform(self, data: dict[str, Any]) -> str:
        device: Device = get_device(data)
        return device.cli_config


def get_abstract_device(infra_device: dict[str, Any]) -> AbstractDevice:
    return AbstractDevice(
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


def get_device(data: dict[str, Any]) -> Device:
    infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
    abstract_device: AbstractDevice = get_abstract_device(infra_device=infra_device)
    return Device(abstract_device=abstract_device)
