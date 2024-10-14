from typing import Any

from models.device_config import (
    AristaDeviceConfig,
    BaseDeviceConfig,
    DefaultDeviceConfig,
)
from models.interfaces_arista import InterfacesConfig
from models.interfaces_oc import (
    AddressesContainer,
    AddressListEntry,
    ConfigContainer,
    ConfigContainerAddressListEntry,
    ConfigContainerIpv4,
    InterfaceListEntry,
    InterfacesContainer,
    Ipv4Container,
    SubinterfaceListEntry,
    SubinterfacesContainer,
)


class Device:
    def __init__(self, abstract_device: dict[str, Any]) -> None:
        self._device: dict[str, Any] = abstract_device
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
                return self.get_arista_device_config()
            case _:
                return self.get_default_device_config()

    def get_default_device_config(self) -> DefaultDeviceConfig:
        interfaces: InterfacesContainer = InterfacesContainer(
            interface=[
                InterfaceListEntry(
                    name=interface.name,
                    config=ConfigContainer(
                        enabled=interface.enabled,
                        description=interface.description
                        if interface.description
                        else "** missing **",
                    ),
                    subinterfaces=SubinterfacesContainer(
                        subinterface=[
                            SubinterfaceListEntry(
                                index=idx,
                                config=ConfigContainer(
                                    enabled=interface.enabled,
                                    description=interface.description
                                    if interface.description
                                    else "** missing **",
                                ),
                                ipv4=Ipv4Container(
                                    addresses=AddressesContainer(
                                        address=[
                                            AddressListEntry(
                                                ip=ip.address.split("/")[0],
                                                config=ConfigContainerAddressListEntry(
                                                    ip=ip.address.split("/")[0],
                                                    prefix_length=ip.address.split("/")[
                                                        1
                                                    ],
                                                ),
                                            )
                                        ]
                                    ),
                                    config=ConfigContainerIpv4(
                                        enabled=interface.enabled,
                                    ),
                                ),
                            )
                            for idx, ip in enumerate(interface.ip_addresses)
                        ]
                    ),
                )
                for interface in self._device.interfaces
            ]
        )
        return DefaultDeviceConfig(interfaces=interfaces)

    def get_arista_device_config(self) -> AristaDeviceConfig:
        interfaces: InterfacesConfig = InterfacesConfig(
            interface=[
                f"interface {interface.name}\n  blah\n"
                for interface in self._device.interfaces
            ]
        )
        return AristaDeviceConfig(interfaces=interfaces)
