import re
from typing import Any

from infrahub_sdk.checks import InfrahubCheck

IS_SLASH_32 = re.compile(r".*\/32$")


class LoopbackCheck(InfrahubCheck):
    query: str = "device_loopback_query"

    def validate(self, data: dict[str, Any]):
        device = data["InfraDevice"]["edges"][0]

        for interface in device["node"]["interfaces"]["edges"]:
            for ip in interface["node"]["ip_addresses"]["edges"]:
                value = ip["node"]["address"].get("value")
                device = device["node"]["name"]["value"]

                if value and not IS_SLASH_32.match(value):
                    self.log_error(
                        message=f"Loopback IP {value} on device {device} must be a /32: {value}",
                        object_id=value,
                        object_type="InfraInterfaceL3",
                    )
