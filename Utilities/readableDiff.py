import re


def readable_diff(diff: str, dict_: dict):
    if len(diff) == 0:
        return

    result = []
    dict_path = list(map(lambda e: e[4:-9], filter(lambda i: i if 'root' in i else None, diff.split())))
    for path in dict_path:
        nums = list(map(int, re.findall(r'\d+', path)))
        section_num, param_num = nums
        result.append(dict_['RACK']['DEVICE']['SECTION'][section_num]['PARAM'][param_num])

    return result
