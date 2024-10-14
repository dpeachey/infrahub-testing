from typing import Any

from models.abstract import AbstractDevice, get_abstract_device
from models.config_arista import AristaDeviceConfig, get_arista_device_config
from models.config_base import BaseDeviceConfig
from models.config_default import DefaultDeviceConfig, get_default_device_config


class Device:
    def __init__(self, device: AbstractDevice) -> None:
        self._device: AbstractDevice = device
        self._device_config: BaseDeviceConfig = self.get_device_config()
        self.name: str = device.name
        self.type: str = device.type

    def json_config(self) -> dict[str, Any]:
        return self._device_config.dict(by_alias=True, exclude_defaults=True)

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


def get_device(data: dict[str, Any]) -> Device:
    infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
    abstract_device: AbstractDevice = get_abstract_device(infra_device=infra_device)
    return Device(device=abstract_device)
