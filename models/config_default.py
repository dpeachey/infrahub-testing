from models.abstract import AbstractDevice
from models.config_base import BaseDeviceConfig
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
from pydantic import Field
from typing_extensions import Annotated


class DefaultDeviceConfig(BaseDeviceConfig):
    interfaces: Annotated[
        InterfacesContainer, Field(None, alias="openconfig-interfaces:interfaces")
    ]


def get_default_device_config(device: AbstractDevice) -> DefaultDeviceConfig:
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
                                                prefix_length=ip.address.split("/")[1],
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
            for interface in device.interfaces
        ]
    )
    return DefaultDeviceConfig(interfaces=interfaces)
