from typing import Any, Self

from models.base import BaseConfigModel
from models.config import (
    AristaDeviceConfig,
    DefaultDeviceConfig,
)
from models.data import DeviceData


class Device:
    def __init__(self, device_data: DeviceData) -> None:
        self._device_data: DeviceData = device_data
        self._device_config: BaseConfigModel = self.get_device_config()
        self.name: str = device_data.name
        self.type: str = device_data.type

    @classmethod
    def create(cls, data: dict[str, Any]) -> Self:
        infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
        device_data: DeviceData = DeviceData.create(infra_device=infra_device)
        return cls(device_data=device_data)

    def json_config(self) -> dict[str, Any]:
        return self._device_config.dict(by_alias=True, exclude_defaults=True)

    def cli_config(self) -> str:
        return self._device_config.cli_config()

    def get_device_config(self) -> BaseConfigModel:
        match self._device_data.platform:
            case "Arista EOS":
                device_config: AristaDeviceConfig = AristaDeviceConfig.create(
                    self._device_data
                )
                return device_config
            case _:
                device_config: DefaultDeviceConfig = DefaultDeviceConfig.create(
                    self._device_data
                )
                return device_config
