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
        )


class BaseDeviceConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def cli_config(self) -> str:
        return f"CLI config is not supported for {type(self).__name__}"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class NokiaVlanIdConfig(BaseConfigModel):
    vlan_id: Annotated[int, Field(None, alias="vlan-id")]


class NokiaSwitchedVlanConfig(BaseConfigModel):
    interface_mode: Annotated[Literal["TRUNK", "ACCESS"], Field(None, alias="interface-mode")]
    vlan: list[NokiaVlanIdConfig]


class NokiaEthernetConfig(BaseConfigModel):
    switched_vlan: Annotated[list[NokiaSwitchedVlanConfig], Field(None, alias="switched-vlan")]


class NokiaInterfaceConfig(BaseConfigModel):
    name: str
    admin_state: Annotated[Literal["enable", "disable"], Field(None, alias="admin-state")]
    ethernet: NokiaEthernetConfig | None = None


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
                        admin_state="enable",
                        ethernet=NokiaEthernetConfig(
                            switched_vlan=[
                                NokiaSwitchedVlanConfig(
                                    interface_mode="TRUNK" if interface.l2_mode == "Trunk" else "Access",
                                    vlan=[NokiaVlanIdConfig(vlan_id=vlan.vlan_id) for vlan in interface.vlans],
                                )
                            ]
                        ),
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


class NokiaDeviceConfig(BaseDeviceConfigModel):
    interfaces: Annotated[NokiaInterfacesConfig, Field(None, alias="interfaces")]

    @classmethod
    def create(cls, device_data: DeviceData) -> Self:
        interfaces: NokiaInterfacesConfig = NokiaInterfacesConfig.create(device_data=device_data)
        return cls(interfaces=interfaces)


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
        return yaml.dump(self._device_config.interfaces.dict(by_alias=True, exclude_defaults=True))


class DeviceTransformYaml(InfrahubTransform):
    query: str = "device_query"
    url: str = "device-yaml"

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        device: Device = Device.create(data)
        return device.yaml_config()
