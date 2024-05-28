"""
из строки 11.1 получить строку 1.11
"""


def comma_wrap(str_: str) -> str:
    str_wth_comma = str_.replace('.', '')
    # format_str = str_wth_comma[0] + '.' + str_wth_comma[1::]
    if len(str_wth_comma) == 2:
        format_str = str_wth_comma + '00.000'
    elif len(str_wth_comma) == 4:
        format_str = str_wth_comma + '.00'
    else:
        format_str = str_wth_comma + '0.00'
    return format_str


def freq_str_create(ch_num: str) -> str:
    return '19' + comma_wrap(ch_num) + '0'
    # return '19' + comma_wrap(ch_num)
