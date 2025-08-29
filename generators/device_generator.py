from typing import Any

from infrahub_sdk.generator import InfrahubGenerator


class DeviceGenerator(InfrahubGenerator):
    async def generate(self, data: dict[str, Any]) -> None:
        site = data["LocationSite"]["edges"][0]["node"]

        device_obj = await self.client.create(
            kind="InfraDevice",
            name=f"{site['name']['value']}-core5",
            description=f"Core router in {site['city']['value']}",
            status="provisioning",
            role="core",
            type="MX204",
            site=site["name"]["value"],
        )
        await device_obj.save(allow_upsert=True)
