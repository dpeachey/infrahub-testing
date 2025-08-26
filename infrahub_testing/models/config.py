from typing import Self

from models.base import BaseDeviceConfigModel
from models.data import DeviceData
from models.interfaces_arista import AristaInterfacesConfig
from models.interfaces_oc import OpenconfigInterfacesConfig
from pydantic import Field
from typing_extensions import Annotated


class DefaultDeviceConfig(BaseDeviceConfigModel):
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


class AristaDeviceConfig(BaseDeviceConfigModel):
    interfaces: AristaInterfacesConfig

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: AristaInterfacesConfig = AristaInterfacesConfig.create(
            device_data=device_data
        )
        return cls(interfaces=interfaces)

    def cli_config(self) -> str:
        return self.interfaces.cli_config()


class DeviceConfig(BaseDeviceConfigModel):
    @staticmethod
    def create(device_data: DeviceData) -> BaseDeviceConfigModel:
        match device_data.platform:
            case "Arista EOS":
                return AristaDeviceConfig.create(device_data)
            case _:
                return DefaultDeviceConfig.create(device_data)
