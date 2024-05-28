def is_instance(data: list[dict] | dict) -> list[str] | str:
    if isinstance(data, list):
        return list(map(lambda d: d.get('operational-state'), data))

    return data.get('operational-state')
