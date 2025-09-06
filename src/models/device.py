from typing import Any, Self

import yaml

from ..helpers.merge import deep_merge
from .base import BaseDeviceConfigModel
from .config import DeviceConfig
from .data import DeviceData


class Device:
    def __init__(self, device_data: DeviceData, templates_path: str) -> None:
        self._templates_path: str = templates_path
        self._device_data: DeviceData = device_data
        self._device_config: BaseDeviceConfigModel = DeviceConfig.create(device_data)
        self.name: str = device_data.name
        self.type: str = device_data.type
        self.role: str = device_data.role

    @classmethod
    def create(cls, data: dict[str, Any], templates_path: str) -> Self:
        infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
        device_data: DeviceData = DeviceData.create(infra_device=infra_device)
        return cls(device_data=device_data, templates_path=templates_path)

    def yaml_config(self) -> dict[str, Any]:
        config = self._device_config.dict(by_alias=True, exclude_defaults=True)

        try:
            with open(f"{self._templates_path}/{self.role}.yaml", "r") as file:
                template = yaml.safe_load(file)
        except FileNotFoundError:
            return "---"

        return yaml.dump(deep_merge(template, config), sort_keys=False)
