from typing import Any, Self

import yaml
from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Literal


class BaseDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IpAddressData(BaseDataModel):
    address: str


class VlanData(BaseDataModel):
    vlan_id: int


class InterfaceData(BaseDataModel):
    name: str
    description: str | None
    enabled: bool
    status: Literal["active", "provisioning"]
    l2_mode: Literal["Access", "Trunk"] | None
    ip_addresses: list[IpAddressData]
    vlans: list[VlanData]


class BgpSessionData(BaseDataModel):
    status: Literal["active", "provisioning"]
    local_ip: str
    remote_ip: str
    local_as: int
    remote_as: int
    peer_group: str


class DeviceData(BaseDataModel):
    name: str
    description: str | None
    platform: str
    type: str
    interfaces: list[InterfaceData]
    bgp_sessions: list[BgpSessionData]

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
                    status=interface["node"]["status"]["value"],
                    l2_mode=interface["node"]["l2_mode"]["value"],
                    ip_addresses=[
                        IpAddressData(address=ip["node"]["address"]["value"])
                        for ip in interface["node"]["ip_addresses"]["edges"]
                    ]
                    if interface["node"].get("ip_addresses")
                    else [],
                    vlans=[
                        VlanData(vlan_id=vlan["node"]["vlan_id"]["value"])
                        for vlan in interface["node"]["tagged_vlan"]["edges"]
                    ]
                    if interface["node"].get("tagged_vlan")
                    else [],
                )
                for interface in infra_device["interfaces"]["edges"]
                if interface["node"].get("l2_mode")
            ]
            if infra_device.get("interfaces")
            else [],
            bgp_sessions=[
                BgpSessionData(
                    status=bgp_session["node"]["status"]["value"],
                    local_ip=bgp_session["node"]["local_ip"]["node"]["address"]["value"].replace("/32", ""),
                    remote_ip=bgp_session["node"]["remote_ip"]["node"]["address"]["value"].replace("/32", ""),
                    local_as=bgp_session["node"]["local_as"]["node"]["asn"]["value"],
                    remote_as=bgp_session["node"]["remote_as"]["node"]["asn"]["value"],
                    peer_group=bgp_session["node"]["peer_group"]["node"]["display_label"],
                )
                for bgp_session in infra_device["bgp_sessions"]["edges"]
            ]
            if infra_device.get("bgp_sessions")
            else [],
        )


class BaseDeviceConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def cli_config(self) -> str:
        return f"CLI config is not supported for {type(self).__name__}"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class NokiaVlanIdConfig(BaseConfigModel):
    vlan_id: Annotated[int, Field(None, alias="vlan-id")]


class NokiaEncapConfig(BaseConfigModel):
    single_tagged: Annotated[NokiaVlanIdConfig, Field(None, alias="single-tagged")]


class NokiaVlanConfig(BaseConfigModel):
    encap: NokiaEncapConfig


class NokiaSubinterfaceConfig(BaseConfigModel):
    index: int
    type: Literal["bridged"]
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    vlan: NokiaVlanConfig


class NokiaInterfaceConfig(BaseConfigModel):
    name: str
    description: str | None = None
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    vlan_tagging: Annotated[bool | None, Field(None, alias="vlan-tagging")] = None
    subinterface: list[NokiaSubinterfaceConfig] | None = None


class NokiaInterfacesConfig(BaseConfigModel):
    """
    Top level container for interfaces.
    """

    interface: list[NokiaInterfaceConfig]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: list[NokiaInterfaceConfig] = []

        for interface in device_data.interfaces:
            if interface.status == "active":
                interfaces.append(
                    NokiaInterfaceConfig(
                        name=interface.name,
                        description=interface.description,
                        admin_state="enable",
                        vlan_tagging=True,
                        subinterface=[
                            NokiaSubinterfaceConfig(
                                index=vlan.vlan_id,
                                type="bridged",
                                admin_state="enable",
                                vlan=NokiaVlanConfig(
                                    encap=NokiaEncapConfig(single_tagged=NokiaVlanIdConfig(vlan_id=vlan.vlan_id))
                                ),
                            )
                            for vlan in interface.vlans
                        ],
                    )
                )
            else:
                interfaces.append(
                    NokiaInterfaceConfig(
                        name=interface.name,
                        admin_state="disable",
                    )
                )

        return cls(interface=interfaces)


class NokiaBgpNeighborConfig(BaseConfigModel):
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    peer_address: Annotated[str, Field(None, alias="peer-address")]
    peer_group: Annotated[str, Field(None, alias="peer-group")]


class NokiaBgpGroupConfig(BaseConfigModel):
    group_name: Annotated[str, Field(None, alias="group-name")]
    peer_as: Annotated[int, Field(None, alias="peer-as")]


class NokiaBgpIPv4UnicastConfig(BaseConfigModel):
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]


class NokiaBgpAfiSafiConfig(BaseConfigModel):
    name: str
    ipv4_unicast: NokiaBgpIPv4UnicastConfig


class NokiaBgpConfig(BaseConfigModel):
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    autonomous_system: Annotated[int, Field(None, alias="autonomous-system")]
    router_id: Annotated[str, Field(None, alias="router-id")]
    afi_safi: Annotated[list[NokiaBgpAfiSafiConfig], Field(None, alias="afi-safi")]
    group: list[NokiaBgpGroupConfig]
    neighbor: list[NokiaBgpNeighborConfig]


class NokiaProtocolsConfig(BaseConfigModel):
    bgp: NokiaBgpConfig


class NokiaNetworkInstanceConfig(BaseConfigModel):
    name: str
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    protocols: NokiaProtocolsConfig


class NokiaNetworkInstancesConfig(BaseConfigModel):
    """
    Top level container for network instances.
    """

    network_instance: Annotated[list[NokiaNetworkInstanceConfig], Field(None, alias="network-instance")]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        network_instances: list[NokiaNetworkInstanceConfig] = []

        for bgp_session in device_data.bgp_sessions:
            if bgp_session.status == "active":
                network_instances.append(
                    NokiaNetworkInstanceConfig(
                        name="deafult",
                        admin_state="enable",
                        protocols=NokiaProtocolsConfig(
                            bgp=NokiaBgpConfig(
                                admin_state="enable",
                                autonomous_system=bgp_session.local_as,
                                router_id=bgp_session.local_ip,
                                afi_safi=[
                                    NokiaBgpAfiSafiConfig(
                                        name="ipv4-unicast",
                                        ipv4_unicast=NokiaBgpIPv4UnicastConfig(admin_state="enable"),
                                    )
                                ],
                                group=[
                                    NokiaBgpGroupConfig(
                                        group_name=bgp_session.peer_group,
                                        peer_as=bgp_session.remote_as,
                                    )
                                ],
                                neighbor=[
                                    NokiaBgpNeighborConfig(
                                        admin_state="enable",
                                        peer_address=bgp_session.remote_ip,
                                        peer_group=bgp_session.peer_group,
                                    )
                                ],
                            )
                        ),
                    )
                )

        return cls(network_instance=network_instances)


class NokiaDeviceConfig(BaseDeviceConfigModel):
    interfaces: Annotated[NokiaInterfacesConfig, Field(None, alias="interfaces")]
    network_instances: Annotated[NokiaNetworkInstancesConfig, Field(None, alias="network-instances")]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: NokiaInterfacesConfig = NokiaInterfacesConfig.create(device_data=device_data)
        network_instances: NokiaNetworkInstancesConfig = NokiaNetworkInstancesConfig.create(device_data=device_data)
        return cls(interfaces=interfaces, network_instances=network_instances)


class DeviceConfig(BaseDeviceConfigModel):
    @staticmethod
    def create(device_data: DeviceData) -> BaseDeviceConfigModel:
        match device_data.platform:
            case "Nokia SR Linux":
                return NokiaDeviceConfig.create(device_data)


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

    def yaml_config(self) -> dict[str, Any]:
        return yaml.dump(self._device_config.dict(by_alias=True, exclude_defaults=True))


class DeviceTransformYaml(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-yaml"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.yaml_config()
