from pydantic import BaseModel, ConfigDict


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    @staticmethod
    def cli_config() -> str:
        return "Not implemented"


class BaseDataModel(BaseModel):
    model_config = ConfigDict(
        extra_fields=False,
    )
