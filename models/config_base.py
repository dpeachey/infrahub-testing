from pydantic import BaseModel, ConfigDict


class BaseDeviceConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    @staticmethod
    def cli_config() -> str:
        return "Not implemented for this device"
