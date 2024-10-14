from models.interfaces_arista import InterfacesConfig
from models.interfaces_oc import InterfacesContainer
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class BaseDeviceConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    @staticmethod
    def cli_config() -> str:
        return "Not implemented for this device"


class DefaultDeviceConfig(BaseDeviceConfig):
    interfaces: Annotated[
        InterfacesContainer, Field(None, alias="openconfig-interfaces:interfaces")
    ]


class AristaDeviceConfig(BaseDeviceConfig):
    interfaces: InterfacesConfig

    def cli_config(self) -> str:
        return self.interfaces.cli_config()
