from typing import Self

from models.abstract import AbstractDevice
from pydantic import BaseModel, ConfigDict


class AristaInterfacesConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    interface: list[str]

    @classmethod
    def create(cls, device: AbstractDevice) -> Self:
        return cls(
            interface=[
                f"interface {interface.name}\n  blah\n"
                for interface in device.interfaces
            ]
        )

    def cli_config(self) -> str:
        return "".join(interface for interface in self.interface)
