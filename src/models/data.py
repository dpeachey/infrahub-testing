from typing import Any, Literal, Self

from .base import BaseDataModel


class IpAddressData(BaseDataModel):
    address: str


class VlanData(BaseDataModel):
    vlan_id: int


class InterfaceData(BaseDataModel):
    name: str
    description: str | None
    enabled: bool
    status: Literal["active", "provisioning", "maintenance"]
    role: Literal["uplink", "leaf", "loopback"]
    l2_mode: Literal["Access", "Trunk"] | None
    ip_addresses: list[IpAddressData]
    vlans: list[VlanData]


class BgpSessionData(BaseDataModel):
    status: Literal["active", "provisioning", "maintenance"]
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
    role: str
    interfaces: list[InterfaceData]
    bgp_sessions: list[BgpSessionData]

    @classmethod
    def create(cls, infra_device: dict[str, Any]) -> Self:
        return cls(
            name=infra_device["name"]["value"],
            description=infra_device["description"]["value"],
            platform=infra_device["platform"]["node"]["name"]["value"],
            type=infra_device["type"]["value"],
            role=infra_device["role"]["value"],
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
