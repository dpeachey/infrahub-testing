from typing import Any, List, Self

import yaml
from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, ConfigDict, Field, RootModel
from typing_extensions import Annotated


class BaseDataModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


class IpAddressData(BaseDataModel):
    address: str


class InterfaceData(BaseDataModel):
    name: str
    description: str | None
    enabled: bool
    ip_addresses: list[IpAddressData]


class DeviceData(BaseDataModel):
    name: str
    description: str | None
    platform: str
    type: str
    interfaces: list[InterfaceData]

    @classmethod
    def create(cls, infra_device: dict[str, Any]) -> Self:
        return cls(
            name=infra_device["name"]["value"],
            description=infra_device["description"]["value"],
            platform=infra_device["platform"]["node"]["name"]["value"],
            type=infra_device["type"]["value"],
            interfaces=[
                InterfaceData(
                    name=interface["node"]["name"]["value"],
                    description=interface["node"]["description"]["value"],
                    enabled=interface["node"]["enabled"]["value"],
                    ip_addresses=[
                        IpAddressData(address=ip["node"]["address"]["value"])
                        for ip in interface["node"]["ip_addresses"]["edges"]
                    ]
                    if interface["node"].get("ip_addresses")
                    else [],
                )
                for interface in infra_device["interfaces"]["edges"]
                if not interface["node"].get("l2_mode")
            ]
            if infra_device.get("interfaces")
            else [],
        )


class BaseDeviceConfigModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    def cli_config(self) -> str:
        return f"CLI config is not supported for {type(self).__name__}"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )


# class AristaInterfacesConfig(BaseConfigModel):
#     interface: list[str]

#     @classmethod
#     def create(cls, device_data: DeviceData) -> Self:
#         return cls(
#             interface=[
#                 (
#                     f"interface {interface.name}\n"
#                     f"   description {interface.description if interface.description else "** missing **"}\n"
#                     "   no switchport\n"
#                     f"   ip address {ip.address}\n"
#                     f"   {'no shutdown' if interface.enabled else 'shutdown'}\n"
#                     "!\n"
#                 )
#                 for interface in device_data.interfaces
#                 for ip in interface.ip_addresses
#             ]
#         )

#     def cli_config(self) -> str:
#         return "".join(interface for interface in self.interface)


class Ipv4AddressType(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    root: Annotated[
        str,
        Field(
            pattern="^(?=^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])){3}$).*$"
        ),
    ]
    """
    An IPv4 address in dotted quad notation using the default
    zone.
    """


class IfindexLeaf(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=0, le=4294967295, title="IfindexLeaf")]
    """
    System assigned number for each interface.  Corresponds to
    ifIndex object in SNMP Interface MIB
    """


class EnabledLeaf(RootModel[bool]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[bool, Field(title="EnabledLeaf")]
    """
    This leaf contains the configured, desired state of the
    interface.

    Systems that implement the IF-MIB use the value of this
    leaf in the 'running' datastore to set
    IF-MIB.ifAdminStatus to 'up' or 'down' after an ifEntry
    has been initialized, as described in RFC 2863.

    Changes in this leaf in the 'running' datastore are
    reflected in ifAdminStatus, but if ifAdminStatus is
    changed over SNMP, this leaf is not affected.
    """


class DescriptionLeaf(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[str, Field(title="DescriptionLeaf")]
    """
    A textual description of the interface.

    A server implementation MAY map this leaf to the ifAlias
    MIB object.  Such an implementation needs to use some
    mechanism to handle the differences in size and characters
    allowed between this leaf and ifAlias.  The definition of
    such a mechanism is outside the scope of this document.

    Since ifAlias is defined to be stored in non-volatile
    storage, the MIB implementation MUST map ifAlias to the
    value of 'description' in the persistently stored
    datastore.

    Specifically, if the device supports ':startup', when
    ifAlias is read the device MUST return the value of
    'description' in the 'startup' datastore, and when it is
    written, it MUST be written to the 'running' and 'startup'
    datastores.  Note that it is up to the implementation to

    decide whether to modify this single leaf in 'startup' or
    perform an implicit copy-config from 'running' to
    'startup'.

    If the device does not support ':startup', ifAlias MUST
    be mapped to the 'description' leaf in the 'running'
    datastore.
    """


class NameLeaf(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[str, Field(title="NameLeaf")]
    """
    The name of the interface.

    A device MAY restrict the allowed values for this leaf,
    possibly depending on the type of the interface.
    For system-controlled interfaces, this leaf is the
    device-specific name of the interface.  The 'config false'
    list interfaces/interface[name]/state contains the currently
    existing interfaces on the device.

    If a client tries to create configuration for a
    system-controlled interface that is not present in the
    corresponding state list, the server MAY reject
    the request if the implementation does not support
    pre-provisioning of interfaces or if the name refers to
    an interface that can never exist in the system.  A
    NETCONF server MUST reply with an rpc-error with the
    error-tag 'invalid-value' in this case.

    The IETF model in RFC 7223 provides YANG features for the
    following (i.e., pre-provisioning and arbitrary-names),
    however they are omitted here:

     If the device supports pre-provisioning of interface
     configuration, the 'pre-provisioning' feature is
     advertised.

     If the device allows arbitrarily named user-controlled
     interfaces, the 'arbitrary-names' feature is advertised.

    When a configured user-controlled interface is created by
    the system, it is instantiated with the same name in the
    /interfaces/interface[name]/state list.
    """


class IpLeaf(RootModel[Ipv4AddressType]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Ipv4AddressType
    """
    The IPv4 address on the interface.
    """


class PrefixLengthLeaf(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=0, le=32, title="Prefix-lengthLeaf")]
    """
    The length of the subnet prefix.
    """


class ConfigContainer(BaseConfigModel):
    """
    Configurable items at the global, physical interface
    level
    """

    description: Annotated[
        DescriptionLeaf, Field(alias="openconfig-interfaces:description")
    ]
    enabled: Annotated[EnabledLeaf, Field(True, alias="openconfig-interfaces:enabled")]


class ConfigContainerSubInterface(BaseConfigModel):
    """
    Configurable items at the global, sub interface
    level
    """

    description: Annotated[
        DescriptionLeaf, Field(alias="openconfig-interfaces:description")
    ]


class ConfigContainerIpv4(BaseConfigModel):
    """
    Configurable items at the global, physical interface
    level
    """

    enabled: Annotated[EnabledLeaf, Field(True, alias="openconfig-interfaces:enabled")]


class ConfigContainerAddressListEntry(BaseConfigModel):
    """
    Configuration data for each configured IPv4
    address on the interface
    """

    ip: Annotated[IpLeaf, Field(None, alias="openconfig-if-ip:ip")]
    prefix_length: Annotated[
        PrefixLengthLeaf, Field(None, alias="openconfig-if-ip:prefix-length")
    ]


class AddressListEntry(BaseConfigModel):
    """
    The list of configured IPv4 addresses on the interface.
    """

    ip: Annotated[IpLeaf, Field(None, alias="openconfig-if-ip:ip")]
    config: Annotated[
        ConfigContainerAddressListEntry, Field(None, alias="openconfig-if-ip:config")
    ]


class AddressesContainer(BaseConfigModel):
    """
    Enclosing container for address list
    """

    address: Annotated[List[AddressListEntry], Field(alias="openconfig-if-ip:address")]


class Ipv4Container(BaseConfigModel):
    """
    Parameters for the IPv4 address family.
    """

    addresses: Annotated[
        AddressesContainer, Field(None, alias="openconfig-if-ip:addresses")
    ]
    config: Annotated[ConfigContainerIpv4, Field(None, alias="openconfig-if-ip:config")]


class SubinterfaceListEntry(BaseConfigModel):
    """
    The list of subinterfaces (logical interfaces) associated
    with a physical interface
    """

    index: Annotated[IfindexLeaf, Field(None, alias="openconfig-interfaces:index")]
    config: Annotated[
        ConfigContainer, Field(None, alias="openconfig-interfaces:config")
    ]
    ipv4: Annotated[Ipv4Container, Field(None, alias="openconfig-if-ip:ipv4")]


class SubinterfacesContainer(BaseConfigModel):
    """
    Enclosing container for the list of subinterfaces associated
    with a physical interface
    """

    subinterface: Annotated[
        List[SubinterfaceListEntry], Field(alias="openconfig-interfaces:subinterface")
    ]


class InterfaceListEntry(BaseConfigModel):
    """
    The list of named interfaces on the device.
    """

    name: Annotated[NameLeaf, Field(None, alias="openconfig-interfaces:name")]
    config: Annotated[
        ConfigContainer, Field(None, alias="openconfig-interfaces:config")
    ]
    subinterfaces: Annotated[
        SubinterfacesContainer, Field(None, alias="openconfig-interfaces:subinterfaces")
    ]


class OpenconfigInterfacesConfig(BaseConfigModel):
    """
    Top level container for interfaces, including configuration
    and state data.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    interface: Annotated[
        List[InterfaceListEntry], Field(alias="openconfig-interfaces:interface")
    ]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        return cls(
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
                for interface in device_data.interfaces
            ]
        )


class DefaultDeviceConfig(BaseDeviceConfigModel):
    interfaces: Annotated[
        OpenconfigInterfacesConfig,
        Field(None, alias="openconfig-interfaces:interfaces"),
    ]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: OpenconfigInterfacesConfig = OpenconfigInterfacesConfig.create(
            device_data=device_data
        )
        return cls(interfaces=interfaces)


class AristaDeviceConfig(BaseDeviceConfigModel):
    interfaces: Annotated[
        OpenconfigInterfacesConfig,
        Field(None, alias="openconfig-interfaces:interfaces"),
    ]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: OpenconfigInterfacesConfig = OpenconfigInterfacesConfig.create(
            device_data=device_data
        )
        return cls(interfaces=interfaces)


class DeviceConfig(BaseDeviceConfigModel):
    @staticmethod
    def create(device_data: DeviceData) -> BaseDeviceConfigModel:
        match device_data.platform:
            case "Arista EOS":
                return AristaDeviceConfig.create(device_data)
            case _:
                return DefaultDeviceConfig.create(device_data)


class Device:
    def __init__(self, device_data: DeviceData) -> None:
        self._device_data: DeviceData = device_data
        self._device_config: BaseDeviceConfigModel = DeviceConfig.create(device_data)
        self.name: str = device_data.name
        self.type: str = device_data.type

    @classmethod
    def create(cls, data: dict[str, Any]) -> Self:
        infra_device: dict[str, Any] = data["InfraDevice"]["edges"][0]["node"]
        device_data: DeviceData = DeviceData.create(infra_device=infra_device)
        return cls(device_data=device_data)

    def json_config(self) -> dict[str, Any]:
        return self._device_config.dict(by_alias=True, exclude_defaults=True)

    def yaml_config(self) -> dict[str, Any]:
        return yaml.dump(self._device_config.dict(exclude_defaults=True))

    # def cli_config(self) -> str:
    #     return self._device_config.cli_config()


class DeviceTransformJson(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-json"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.json_config()


class DeviceTransformYaml(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-yaml"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.yaml_config()


# class DeviceTransformCli(InfrahubTransform):
#     query: str = "device_query"
#     url: str = "device-cli"

#     async def transform(self, data: dict[str, Any]) -> str:
#         device: Device = Device.create(data)
#         return device.cli_config()
