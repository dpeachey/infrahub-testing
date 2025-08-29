from typing import Any

from infrahub_sdk.transforms import InfrahubTransform

from ..models.device import Device


class DeviceTransformYaml(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-yaml"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        templates_path = f"{self.root_directory}/src/transforms/templates"
        device: Device = Device.create(data=data, templates_path=templates_path)
        return device.yaml_config()
