import sys

sys.path.append(".")
from typing import Any

from infrahub_sdk.transforms import InfrahubTransform
from models.device import Device


class DeviceTransformJson(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-json"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.json_config()


class DeviceTransformCli(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-cli"

    async def transform(self, data: dict[str, Any]) -> str:
        device: Device = Device.create(data)
        return device.cli_config()
