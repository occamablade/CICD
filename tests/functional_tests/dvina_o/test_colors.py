import logging
from enum import Enum

import pytest

logger = logging.getLogger(__name__)


class Colors(Enum):
    GREEN = 1
    RED = 2
    YELLOW = 3
    GREY = 0


class TestColors:

    @pytest.mark.parametrize(
        'color, status_color_fixture',
        [
            (Colors.GREEN.value, 1), (Colors.YELLOW.value, 2), (Colors.RED.value, 3)
        ],
        indirect=['status_color_fixture'],
        ids=[
            'Check green color for status',
            'Check yellow color for status',
            'Check red color for status'
        ]
    )
    def test_status_colors(self, color: int, status_color_fixture: int):
        """
        Подразумевается что плата настроена и ее статус изначально зеленый
        """
        assert status_color_fixture == color, f'Цвет не совпадает: {status_color_fixture}'

    @pytest.mark.parametrize(
        'color, line_color_fixture',
        [
            (Colors.GREEN.value, 1), (Colors.YELLOW.value, 2), (Colors.RED.value, 3), (Colors.GREY.value, 4)
        ],
        indirect=['line_color_fixture'],
        ids=[
            'Check green color for line',
            'Check yellow color for line',
            'Check red color for line',
            'Check grey color for line'
        ]
    )
    def test_line_colors(self, color: int, line_color_fixture: list):
        """
        Подразумевается что плата настроена и ее статус изначально зеленый
        """
        assert all(map(lambda c: c == color,
                       line_color_fixture)), f'Цвета не совпадают: {all(map(lambda c: c == color, line_color_fixture))}'

    @pytest.mark.parametrize(
        'color, client_color_fixture',
        [
            (Colors.GREEN.value, 1), (Colors.YELLOW.value, 2), (Colors.RED.value, 3), (Colors.GREY.value, 4)
        ],
        indirect=['client_color_fixture'],
        ids=[
            'Check green color for client',
            'Check yellow color for client',
            'Check red color for client',
            'Check grey color for client'
        ]
    )
    def test_client_colors(self, color: int, client_color_fixture: list):
        """
        Подразумевается что плата настроена и ее статус изначально зеленый
        """
        assert all(map(lambda c: c == color, client_color_fixture)), \
            f'Цвета не совпадают: {all(map(lambda c: c == color, client_color_fixture))}'
