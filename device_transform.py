from infrahub_sdk.transforms import InfrahubTransform


class DeviceTransform(InfrahubTransform):

    query = "device_query"
    url = "device"

    async def transform(self, data):
        device = data["InfraDevice"]["edges"][0]["node"]
        device_name = device["name"]["value"]
        device_description = device["description"]["value"]
        device_type = device["type"]["value"]
        site_name = device["site"]["node"]["name"]["value"]

        return {
            "device_name": device_name,
            "device_description": device_description,
            "device_type": device_type,
            "site_name": site_name
        }
