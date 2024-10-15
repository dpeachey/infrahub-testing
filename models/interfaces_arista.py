from typing import Self

from models.data import DeviceData
from pydantic import BaseModel, ConfigDict


class AristaInterfacesConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
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
