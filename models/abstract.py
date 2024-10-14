from pydantic import BaseModel, ConfigDict


class AbstractBaseModel(BaseModel):
    model_config = ConfigDict(
        extra_fields=False,
    )


class AbstractIpAddress(AbstractBaseModel):
    address: str


class AbstractInterface(AbstractBaseModel):
    name: str
    description: str | None
    enabled: bool
    ip_addresses: list[AbstractIpAddress]


class AbstractDevice(AbstractBaseModel):
    name: str
    description: str | None
    platform: str
    type: str
    interfaces: list[AbstractInterface]
