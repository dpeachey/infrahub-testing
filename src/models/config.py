from typing import Literal, Self

from pydantic import Field
from typing_extensions import Annotated

from .base import BaseConfigModel, BaseDeviceConfigModel
from .data import DeviceData


class NokiaVlanIdConfig(BaseConfigModel):
    vlan_id: Annotated[int, Field(None, alias="vlan-id")]


class NokiaEncapConfig(BaseConfigModel):
    single_tagged: Annotated[NokiaVlanIdConfig, Field(None, alias="single-tagged")]


class NokiaVlanConfig(BaseConfigModel):
    encap: NokiaEncapConfig


class NokiaIpPrefixConfig(BaseConfigModel):
    ip_prefix: Annotated[str, Field(None, alias="ip-prefix")]


class NokiaIpAddressConfig(BaseConfigModel):
    address: list[NokiaIpPrefixConfig]


class NokiaSubinterfaceConfig(BaseConfigModel):
    match_field: str = "index"
    index: int
    type: Literal["bridged"] | None = None
    admin_state: Annotated[Literal["enable", "disable"] | None, Field(None, alias="admin-state")] = None
    vlan: NokiaVlanConfig | None = None
    ipv4: NokiaIpAddressConfig | None = None
    ipv6: NokiaIpAddressConfig | None = None


class NokiaInterfaceConfig(BaseConfigModel):
    match_field: str = "name"
    name: str
    description: str = ""
    admin_state: Annotated[Literal["enable", "disable"] | None, Field(None, alias="admin-state")] = None
    vlan_tagging: Annotated[bool | None, Field(None, alias="vlan-tagging")] = None
    subinterface: list[NokiaSubinterfaceConfig] | None = None

    @classmethod
    def create(cls, device_data: DeviceData) -> list[Self]:
        interfaces: list[Self] = []

        for interface in device_data.interfaces:
            match interface.role:
                case "uplink":
                    interfaces.append(
                        cls(
                            name=interface.name,
                            description=interface.description,
                            admin_state="enable" if interface.status == "active" else "disable",
                        )
                    )
                case "loopback":
                    interfaces.append(
                        cls(
                            name=interface.name,
                            subinterface=[
                                NokiaSubinterfaceConfig(
                                    index=0,
                                    ipv4=NokiaIpAddressConfig(
                                        address=[
                                            NokiaIpPrefixConfig(
                                                ip_prefix=ip.address,
                                            )
                                            for ip in interface.ip_addresses
                                            if ip.address.endswith("/32")
                                        ]
                                    ),
                                    ipv6=NokiaIpAddressConfig(
                                        address=[
                                            NokiaIpPrefixConfig(
                                                ip_prefix=ip.address,
                                            )
                                            for ip in interface.ip_addresses
                                            if ip.address.endswith("/128")
                                        ]
                                    ),
                                )
                            ],
                        )
                    )

        return interfaces


class NokiaIsisInstanceConfig(BaseConfigModel):
    name: str
    net: list[str]


class NokiaIsisConfig(BaseConfigModel):
    instance: list[NokiaIsisInstanceConfig]


class NokiaBgpNeighborConfig(BaseConfigModel):
    peer_address: Annotated[str, Field(None, alias="peer-address")]
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    peer_group: Annotated[str, Field(None, alias="peer-group")]


class NokiaBgpGroupConfig(BaseConfigModel):
    group_name: Annotated[str, Field(None, alias="group-name")]
    peer_as: Annotated[int, Field(None, alias="peer-as")]


class NokiaBgpConfig(BaseConfigModel):
    router_id: Annotated[str, Field(None, alias="router-id")]
    autonomous_system: Annotated[int, Field(None, alias="autonomous-system")]
    neighbor: list[NokiaBgpNeighborConfig]
    group: list[NokiaBgpGroupConfig]


class NokiaProtocolsConfig(BaseConfigModel):
    bgp: Annotated[NokiaBgpConfig, Field(None, alias="srl_nokia-bgp:bgp")]
    isis: Annotated[NokiaIsisConfig, Field(None, alias="srl_nokia-isis:isis")]


class NokiaNetworkInstanceConfig(BaseConfigModel):
    match_field: str = "name"
    name: str
    protocols: NokiaProtocolsConfig

    @classmethod
    def create(cls, device_data: DeviceData) -> list[Self]:
        network_instances: list[Self] = []
        router_id = ""
        isis_net_id = ""

        for interface in device_data.interfaces:
            if interface.role == "loopback":
                for ip in interface.ip_addresses:
                    if "/32" in ip.address:
                        ip = ip.address.replace("/32", "")
                        last_octet = ip.split(".")[-1]
                        router_id = ip
                        isis_net_id = f"49.0001.0000.0000.{last_octet.zfill(4)}.00"
                        break

        if device_data.bgp_sessions:
            network_instances.append(
                cls(
                    name="default",
                    protocols=NokiaProtocolsConfig(
                        isis=NokiaIsisConfig(
                            instance=[NokiaIsisInstanceConfig(name="ISIS", net=[isis_net_id])],
                        ),
                        bgp=NokiaBgpConfig(
                            router_id=router_id,
                            autonomous_system=device_data.bgp_sessions[0].local_as,
                            group=[
                                NokiaBgpGroupConfig(
                                    group_name=bgp_session.peer_group,
                                    peer_as=bgp_session.remote_as,
                                )
                                for bgp_session in device_data.bgp_sessions
                                if bgp_session.status == "active"
                            ],
                            neighbor=[
                                NokiaBgpNeighborConfig(
                                    admin_state="enable",
                                    peer_address=bgp_session.remote_ip.replace("/128", ""),
                                    peer_group=bgp_session.peer_group,
                                )
                                for bgp_session in device_data.bgp_sessions
                                if bgp_session.status == "active"
                            ],
                        ),
                    ),
                )
            )

        return network_instances


class NokiaDeviceConfig(BaseDeviceConfigModel):
    interface: Annotated[list[NokiaInterfaceConfig], Field(None, alias="srl_nokia-interfaces:interface")]
    network_instance: Annotated[
        list[NokiaNetworkInstanceConfig], Field(None, alias="srl_nokia-network-instance:network-instance")
    ]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interface: NokiaInterfaceConfig = NokiaInterfaceConfig.create(device_data=device_data)
        network_instance: NokiaNetworkInstanceConfig = NokiaNetworkInstanceConfig.create(device_data=device_data)
        return cls(interface=interface, network_instance=network_instance)


class DeviceConfig(BaseDeviceConfigModel):
    @staticmethod
    def create(device_data: DeviceData) -> BaseDeviceConfigModel:
        match device_data.platform:
            case "Nokia SR Linux":
                return NokiaDeviceConfig.create(device_data)
