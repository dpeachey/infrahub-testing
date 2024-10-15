from typing import Any, Self

from models.abstract import AbstractDevice
from models.config import (
    AristaDeviceConfig,
    BaseDeviceConfig,
    DefaultDeviceConfig,
)


class Device:
    def __init__(self, device: AbstractDevice) -> None:
        self._device: AbstractDevice = device
        self._device_config: BaseDeviceConfig = self.get_device_config()
        self.name: str = device.name
        self.type: str = device.type

    @classmethod
    def create(cls, data: dict[str, Any]) -> Self:
        infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
        abstract_device: AbstractDevice = AbstractDevice.create(
            infra_device=infra_device
        )
        return cls(device=abstract_device)

    def json_config(self) -> dict[str, Any]:
        return self._device_config.dict(by_alias=True, exclude_defaults=True)

    def cli_config(self) -> str:
        return self._device_config.cli_config()

    def get_device_config(self) -> BaseDeviceConfig:
        match self._device.platform:
            case "Arista EOS":
                device_config: AristaDeviceConfig = AristaDeviceConfig.create(
                    self._device
                )
                return device_config
            case _:
                device_config: DefaultDeviceConfig = DefaultDeviceConfig.create(
                    self._device
                )
                return device_config
