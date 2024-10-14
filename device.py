from typing import Any

from models.abstract import AbstractDevice
from models.device_config import (
    AristaDeviceConfig,
    BaseDeviceConfig,
    DefaultDeviceConfig,
    get_arista_device_config,
    get_default_device_config,
)


class Device:
    def __init__(self, abstract_device: AbstractDevice) -> None:
        self._device: AbstractDevice = abstract_device
        self._device_config: BaseDeviceConfig = self.get_device_config()
        self.name: str = abstract_device.name
        self.type: str = abstract_device.type

    @property
    def json_config(self) -> dict[str, Any]:
        return self._device_config.dict(by_alias=True, exclude_defaults=True)

    @property
    def cli_config(self) -> str:
        return self._device_config.cli_config()

    def get_device_config(self) -> BaseDeviceConfig:
        match self._device.platform:
            case "Arista EOS":
                device_config: AristaDeviceConfig = get_arista_device_config(
                    self._device
                )
                return device_config
            case _:
                device_config: DefaultDeviceConfig = get_default_device_config(
                    self._device
                )
                return device_config
