from typing import Any

from infrahub_sdk import InfrahubClientSync
from infrahub_sdk.generator import InfrahubGenerator


class DeviceArtifactGenerator(InfrahubGenerator):
    async def generate(self, data: dict[str, Any]) -> None:
        device_name = data["InfraInterfaceL3"]["edges"][0]["node"]["device"]["node"]["name"]["value"]
        client = InfrahubClientSync()
        device = client.get(kind="InfraDevice", name__value=device_name)
        device.artifact_generate(name="Device config YAML")
