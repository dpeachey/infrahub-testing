from infrahub_sdk.transforms import InfrahubTransform


class DeviceTransform(InfrahubTransform):

    query = "device_query"
    url = "device"

    async def transform(self, data):
        device = data["InfraDevice"]["edges"][0]["node"]
        device_name = device["name"]["value"]
        device_description = device["description"]["value"]
        device_type = device["type"]["value"]
        site = device["site"]["node"]
        site_name = site["name"]["value"]
        site_vlan_ids = [vlan["node"]["vlan_id"]["value"] for vlan in site["vlans"]["edges"]]

        return {
            "device_name": device_name,
            "device_description": device_description,
            "device_type": device_type,
            "site_name": site_name,
            "site_vlan_ids": site_vlan_ids
        }

        # return (
        #     f"Device: {device_name}\n"
        #     f"Description: {device_description}\n"
        #     f"Type: {device_type}\n"
        #     f"Site: {site_name}\n"
        #     f"VLAN IDs: {','.join(str(vlan_id) for vlan_id in site_vlan_ids)}"
        # )
