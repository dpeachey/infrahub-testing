from typing import List, Self

from models.abstract import AbstractDevice
from pydantic import BaseModel, ConfigDict, Field, RootModel
from typing_extensions import Annotated


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


class ConfigContainer(BaseModel):
    """
    Configurable items at the global, physical interface
    level
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    description: Annotated[
        DescriptionLeaf, Field(alias="openconfig-interfaces:description")
    ]
    enabled: Annotated[EnabledLeaf, Field(True, alias="openconfig-interfaces:enabled")]


class ConfigContainerIpv4(BaseModel):
    """
    Configurable items at the global, physical interface
    level
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    enabled: Annotated[EnabledLeaf, Field(True, alias="openconfig-interfaces:enabled")]


class ConfigContainerAddressListEntry(BaseModel):
    """
    Configuration data for each configured IPv4
    address on the interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    ip: Annotated[IpLeaf, Field(None, alias="openconfig-if-ip:ip")]
    prefix_length: Annotated[
        PrefixLengthLeaf, Field(None, alias="openconfig-if-ip:prefix-length")
    ]


class AddressListEntry(BaseModel):
    """
    The list of configured IPv4 addresses on the interface.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    ip: Annotated[IpLeaf, Field(None, alias="openconfig-if-ip:ip")]
    config: Annotated[
        ConfigContainerAddressListEntry, Field(None, alias="openconfig-if-ip:config")
    ]


class AddressesContainer(BaseModel):
    """
    Enclosing container for address list
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    address: Annotated[List[AddressListEntry], Field(alias="openconfig-if-ip:address")]


class Ipv4Container(BaseModel):
    """
    Parameters for the IPv4 address family.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    addresses: Annotated[
        AddressesContainer, Field(None, alias="openconfig-if-ip:addresses")
    ]
    config: Annotated[ConfigContainerIpv4, Field(None, alias="openconfig-if-ip:config")]


class SubinterfaceListEntry(BaseModel):
    """
    The list of subinterfaces (logical interfaces) associated
    with a physical interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    index: Annotated[IfindexLeaf, Field(None, alias="openconfig-interfaces:index")]
    config: Annotated[
        ConfigContainer, Field(None, alias="openconfig-interfaces:config")
    ]
    ipv4: Annotated[Ipv4Container, Field(None, alias="openconfig-if-ip:ipv4")]


class SubinterfacesContainer(BaseModel):
    """
    Enclosing container for the list of subinterfaces associated
    with a physical interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    subinterface: Annotated[
        List[SubinterfaceListEntry], Field(alias="openconfig-interfaces:subinterface")
    ]


class InterfaceListEntry(BaseModel):
    """
    The list of named interfaces on the device.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    name: Annotated[NameLeaf, Field(None, alias="openconfig-interfaces:name")]
    config: Annotated[
        ConfigContainer, Field(None, alias="openconfig-interfaces:config")
    ]
    subinterfaces: Annotated[
        SubinterfacesContainer, Field(None, alias="openconfig-interfaces:subinterfaces")
    ]


class OpenconfigInterfacesConfig(BaseModel):
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
    def create(cls, device: AbstractDevice) -> Self:
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
                for interface in device.interfaces
            ]
        )
