from pydantic import BaseModel, ConfigDict


class BaseDeviceConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def cli_config(self) -> str:
        return f"CLI config is not supported for {type(self).__name__}"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BaseDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
