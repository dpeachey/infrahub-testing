from models.abstract import AbstractDevice
from models.config_base import BaseDeviceConfig
from models.interfaces_arista import InterfacesConfig


class AristaDeviceConfig(BaseDeviceConfig):
    interfaces: InterfacesConfig

    def cli_config(self) -> str:
        return self.interfaces.cli_config()


def get_arista_device_config(device: AbstractDevice) -> AristaDeviceConfig:
    interfaces: InterfacesConfig = InterfacesConfig(
        interface=[
            f"interface {interface.name}\n  blah\n" for interface in device.interfaces
        ]
    )
    return AristaDeviceConfig(interfaces=interfaces)
