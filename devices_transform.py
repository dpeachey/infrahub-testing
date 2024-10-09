from infrahub_sdk.transforms import InfrahubTransform


class DevicesTransform(InfrahubTransform):

    query = "devices_query"
    url = "devices"

    async def transform(self, data):
        device = data["InfraDevice"]["edges"][0]["node"]
        device_name = device["name"]["value"]
        device_description = device["description"]["value"]
        device_type = device["type"]["value"]

        return {
            "device_name": device_name,
            "device_description": device_description,
            "device_type": device_type
        }
