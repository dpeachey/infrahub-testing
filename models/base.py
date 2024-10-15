from pydantic import BaseModel, ConfigDict


class BaseDeviceConfigModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    @staticmethod
    def cli_config() -> str:
        return "CLI config is not supported for this device"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )


class BaseDataModel(BaseModel):
    model_config = ConfigDict(
        extra_fields=False,
    )
