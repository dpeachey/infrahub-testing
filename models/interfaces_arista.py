from pydantic import BaseModel, ConfigDict


class InterfacesConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    interface: list[str]

    def cli_config(self) -> str:
        return "".join(interface for interface in self.interface)
