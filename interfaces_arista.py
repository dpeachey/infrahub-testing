from typing import Self

from base import BaseConfigModel
from data import DeviceData


class AristaInterfacesConfig(BaseConfigModel):
    interface: list[str]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        return cls(
            interface=[
                f"interface {interface.name}\n  blah\n"
                for interface in device_data.interfaces
            ]
        )

    def cli_config(self) -> str:
        return "".join(interface for interface in self.interface)
