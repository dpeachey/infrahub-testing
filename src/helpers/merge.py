import copy

LIST_MERGE_ID_KEYS = ["name", "index", "sequence-id", "group-name", "peer-address"]


def find_id_key(list_of_dicts):
    """Finds a suitable unique identifier key from the first item in a list of dicts."""
    if not list_of_dicts or not isinstance(list_of_dicts[0], dict):
        return None

    first_item_keys = list_of_dicts[0].keys()
    for key in LIST_MERGE_ID_KEYS:
        if key in first_item_keys:
            return key
    return None


def merge_lists(base_list, override_list):
    """
    Merges two lists. If they are lists of dictionaries, it merges them based
    on a unique key. Otherwise, the override list replaces the base list.
    """
    if not override_list:
        return base_list

    id_key = find_id_key(override_list)

    # If we can't identify items by a key, the override list replaces the base list.
    if not id_key:
        return override_list

    # Create a map of the override list items for efficient lookup.
    override_map = {item.get(id_key): item for item in override_list if isinstance(item, dict) and id_key in item}

    final_list = []

    # Iterate through the base list to merge existing items.
    for base_item in base_list:
        if not isinstance(base_item, dict):
            final_list.append(base_item)
            continue

        item_id = base_item.get(id_key)

        # If a corresponding item exists in the override list, merge them.
        if item_id is not None and item_id in override_map:
            override_item = override_map.pop(item_id)  # Pop to track new items.
            final_list.append(deep_merge(base_item, override_item))
        else:
            # Otherwise, keep the base item as is.
            final_list.append(base_item)

    # Add any new items from the override list that were not in the base list.
    final_list.extend(override_map.values())

    return final_list


def deep_merge(base, override):
    """
    Recursively merges two data structures (dictionaries or lists).
    - 'override' values take precedence over 'base' values.
    - Dictionaries are merged recursively.
    - Lists are merged using the `merge_lists` function.
    """
    merged = copy.deepcopy(base)

    for key, override_value in override.items():
        if key in merged:
            base_value = merged[key]
            if isinstance(base_value, dict) and isinstance(override_value, dict):
                merged[key] = deep_merge(base_value, override_value)
            elif isinstance(base_value, list) and isinstance(override_value, list):
                merged[key] = merge_lists(base_value, override_value)
            else:
                merged[key] = override_value
        else:
            merged[key] = override_value

    return merged
