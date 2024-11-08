import re
from typing import Any

from infrahub_sdk.checks import InfrahubCheck

IS_SLASH_32 = re.compile(r".*\/32$")


class LoopbackCheck(InfrahubCheck):
    query: str = "loopback_query"

    def validate(self, data: dict[str, Any]):
        for interface in data["InfraInterfaceL3"]["edges"]:
            for ip in interface["node"]["ip_addresses"]["edges"]:
                value = ip["node"]["address"].get("value")
                if value and not IS_SLASH_32.match(value):
                    self.log_error(
                        message=f"Loopback IP must be a /32: {value}",
                        object_id=value,
                        object_type="InfraInterfaceL3",
                    )
