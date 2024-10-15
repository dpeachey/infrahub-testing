from typing import Self

from models.base import BaseConfigModel
from models.data import DeviceData
from models.interfaces_arista import AristaInterfacesConfig
from models.interfaces_oc import OpenconfigInterfacesConfig
from pydantic import Field
from typing_extensions import Annotated


class DefaultDeviceConfig(BaseConfigModel):
    interfaces: Annotated[
        OpenconfigInterfacesConfig,
        Field(None, alias="openconfig-interfaces:interfaces"),
    ]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: OpenconfigInterfacesConfig = OpenconfigInterfacesConfig.create(
            device_data=device_data
        )
        return cls(interfaces=interfaces)


class AristaDeviceConfig(BaseConfigModel):
    interfaces: AristaInterfacesConfig

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: AristaInterfacesConfig = AristaInterfacesConfig.create(
            device_data=device_data
        )
        return cls(interfaces=interfaces)

    def cli_config(self) -> str:
        return self.interfaces.cli_config()
