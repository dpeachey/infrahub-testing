from typing import Self

from models.abstract import AbstractDevice
from models.interfaces_arista import AristaInterfacesConfig
from models.interfaces_oc import OpenconfigInterfacesConfig
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
        OpenconfigInterfacesConfig,
        Field(None, alias="openconfig-interfaces:interfaces"),
    ]

    @classmethod
    def create(cls, device: AbstractDevice) -> Self:
        interfaces: OpenconfigInterfacesConfig = OpenconfigInterfacesConfig.create(
            device=device
        )
        return cls(interfaces=interfaces)


class AristaDeviceConfig(BaseDeviceConfig):
    interfaces: AristaInterfacesConfig

    @classmethod
    def create(cls, device: AbstractDevice) -> Self:
        interfaces: AristaInterfacesConfig = AristaInterfacesConfig.create(
            device=device
        )
        return cls(interfaces=interfaces)

    def cli_config(self) -> str:
        return self.interfaces.cli_config()
