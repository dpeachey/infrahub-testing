import copy
import logging
from typing import Any, Self

import yaml
from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Literal

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
LIST_MERGE_ID_KEYS = ["name", "index", "sequence-id", "peer-address"]


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
    role: Literal["uplink", "leaf", "loopback"]
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
                    role=interface["node"]["role"]["value"],
                    l2_mode=interface["node"]["l2_mode"]["value"] if interface["node"].get("l2_mode") else None,
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
    description: str | None = None
    admin_state: Annotated[Literal["enable", "disable"] | None, Field(None, alias="admin-state")] = None
    vlan_tagging: Annotated[bool | None, Field(None, alias="vlan-tagging")] = None
    subinterface: list[NokiaSubinterfaceConfig] | None = None

    @classmethod
    def create(cls, device_data: DeviceData) -> list[Self]:
        interfaces: list[Self] = []

        for interface in device_data.interfaces:
            if interface.status == "active":
                match interface.role:
                    case "uplink":
                        interfaces.append(
                            cls(
                                name=interface.name,
                                description=interface.description,
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


class NokiaBgpNeighborConfig(BaseConfigModel):
    peer_address: Annotated[str, Field(None, alias="peer-address")]
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    peer_group: Annotated[str, Field(None, alias="peer-group")]


class NokiaBgpConfig(BaseConfigModel):
    router_id: Annotated[str, Field(None, alias="router-id")]
    neighbor: list[NokiaBgpNeighborConfig]


class NokiaProtocolsConfig(BaseConfigModel):
    bgp: Annotated[NokiaBgpConfig, Field(None, alias="srl_nokia-bgp:bgp")]


class NokiaNetworkInstanceConfig(BaseConfigModel):
    match_field: str = "name"
    name: str
    protocols: NokiaProtocolsConfig

    @classmethod
    def create(cls, device_data: DeviceData) -> list[Self]:
        network_instances: list[Self] = []
        router_id = ""

        for interface in device_data.interfaces:
            if interface.role == "loopback":
                for ip in interface.ip_addresses:
                    if "/32" in ip.address:
                        router_id = ip.address.replace("/32", "")
                        break

        network_instances.append(
            cls(
                name="default",
                protocols=NokiaProtocolsConfig(
                    bgp=NokiaBgpConfig(
                        router_id=router_id,
                        neighbor=[
                            NokiaBgpNeighborConfig(
                                admin_state="enable",
                                peer_address=bgp_session.remote_ip.replace("/128", ""),
                                peer_group=bgp_session.peer_group,
                            )
                            for bgp_session in device_data.bgp_sessions
                            if bgp_session.status == "active"
                        ],
                    )
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
        config = self._device_config.dict(by_alias=True, exclude_defaults=True)

        with open("template_leaf.yaml", "r") as file:
            template = yaml.safe_load(file)

        return yaml.dump(deep_merge(template, config), sort_keys=False)


class DeviceTransformYaml(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-yaml"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.yaml_config()


def find_id_key(list_of_dicts):
    """Finds a suitable unique identifier key from the first item in a list of dicts."""
    if not list_of_dicts or not isinstance(list_of_dicts[0], dict):
        return None

    first_item_keys = list_of_dicts[0].keys()
    for key in LIST_MERGE_ID_KEYS:
        if key in first_item_keys:
            return key
    return None


def merge_lists(base_list, override_list):
    """
    Merges two lists. If they are lists of dictionaries, it merges them based
    on a unique key. Otherwise, the override list replaces the base list.
    """
    if not override_list:
        return base_list

    id_key = find_id_key(override_list)

    # If we can't identify items by a key, the override list replaces the base list.
    if not id_key:
        return override_list

    # Create a map of the override list items for efficient lookup.
    override_map = {item.get(id_key): item for item in override_list if isinstance(item, dict) and id_key in item}

    final_list = []

    # Iterate through the base list to merge existing items.
    for base_item in base_list:
        if not isinstance(base_item, dict):
            final_list.append(base_item)
            continue

        item_id = base_item.get(id_key)

        # If a corresponding item exists in the override list, merge them.
        if item_id is not None and item_id in override_map:
            override_item = override_map.pop(item_id)  # Pop to track new items.
            final_list.append(deep_merge(base_item, override_item))
        else:
            # Otherwise, keep the base item as is.
            final_list.append(base_item)

    # Add any new items from the override list that were not in the base list.
    final_list.extend(override_map.values())

    return final_list


def deep_merge(base, override):
    """
    Recursively merges two data structures (dictionaries or lists).
    - 'override' values take precedence over 'base' values.
    - Dictionaries are merged recursively.
    - Lists are merged using the `merge_lists` function.
    """
    merged = copy.deepcopy(base)

    for key, override_value in override.items():
        if key in merged:
            base_value = merged[key]
            if isinstance(base_value, dict) and isinstance(override_value, dict):
                merged[key] = deep_merge(base_value, override_value)
            elif isinstance(base_value, list) and isinstance(override_value, list):
                merged[key] = merge_lists(base_value, override_value)
            else:
                merged[key] = override_value
        else:
            merged[key] = override_value

    return merged
