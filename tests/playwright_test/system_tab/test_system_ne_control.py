import logging

import pytest

from Utilities.all import NODE_NAME, CHANGE_IP, NODE_NAME1, TEST_NODE, NODE_LIST_FOR_MASS_OPS

logger = logging.getLogger(__name__)


class TestSystemTabNeControl:

    def test_system_tab_ne_control_setup(self, system_tab_ne_control_setup):
        pass

    def test_open_ne_control_tab_t618(self, ne_control_fixture_T618):
        assert ne_control_fixture_T618 == 'Add Node', f'Тест-кейс T618 не прошёл'
        logger.warning('Успешно зашли на вкладку NE Control')
        logger.info('Тест-кейс T618 прошёл успешно')

    def test_create_new_ne_t622(self, create_new_ne_t622):
        assert TEST_NODE['node_name'] in create_new_ne_t622, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не добавлен'
        logger.warning(f'Новый сетевой элемент [ {TEST_NODE["node_name"]} ] успешно добавлен')
        logger.info('Тест-кейс T622 прошёл успешно')

    def test_lock_ne_t624(self, lock_ne_via_ne_control_fixture_t624):
        assert lock_ne_via_ne_control_fixture_t624 == 'locked', f'Узел [ {TEST_NODE["node_name"]} ] не заблокирован'
        logger.warning(f'Узел [ {TEST_NODE["node_name"]} ] успешно заблокирован')
        logger.info('Тест-кейс T624 прошёл успешно')

    def test_unlock_ne_t626(self, unlock_ne_via_ne_control_fixture_t626):
        assert unlock_ne_via_ne_control_fixture_t626 == 'unlocked', f'Узел [ {TEST_NODE["node_name"]} ] не разблокирован'
        logger.warning(f'Узел [ {TEST_NODE["node_name"]} ] успешно разблокирован')
        logger.info('Тест-кейс T626 прошёл успешно')

    @pytest.mark.skip(reason="Not Implemented")
    def test_lock_ne_via_menu_t629(self):
        pass

    @pytest.mark.skip(reason="Not Implemented")
    def test_unlock_ne_via_menu_t630(self):
        pass

    def test_delete_ne_t638(self, delete_ne_t638):
        assert TEST_NODE["node_name"] not in delete_ne_t638, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не удалён'
        logger.warning(f'Новый сетевой элемент [ {TEST_NODE["node_name"]} ] успешно удалён')
        logger.info('Тест-кейс T638 прошёл успешно')

    def test_create_new_ne_via_context_menu_t623(self, create_new_ne_via_context_menu_t623):
        assert TEST_NODE["node_name"] in create_new_ne_via_context_menu_t623, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не добавлен'
        logger.warning(f'Новый сетевой элемент [ {TEST_NODE["node_name"]} ] успешно добавлен')
        logger.info('Тест-кейс T623 прошёл успешно')

    def test_edit_name_ne_t627(self, edit_name_ne_fixture_t627):
        assert TEST_NODE["node_name"] + '_1' in edit_name_ne_fixture_t627, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не переименован'
        logger.warning(f'Сетевой элемент [ {TEST_NODE["node_name"]} ] успешно переименован на [ {TEST_NODE["node_name"] + "_1"} ]')
        logger.info('Тест-кейс T627 прошёл успешно')

    def test_edit_domain_t628(self, edit_ne_domain_fixture_t628):
        assert edit_ne_domain_fixture_t628 == "Beeline", f'Домен для сетевого элемента [ {TEST_NODE["node_name"]} ] не изменен'
        logger.warning(f'Домен узла  [ {TEST_NODE["node_name"]} ] успешно переименован на [ education ]')
        logger.info('Тест-кейс T627 прошёл успешно')

    def test_edit_login_for_ne_t632(self, edit_login_for_ne_fixture_t632):
        assert TEST_NODE["node_name"] in edit_login_for_ne_fixture_t632, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не найден'
        logger.warning(f'Сетевой элемент [ {TEST_NODE["node_name"]} ] найден')
        logger.info('Тест-кейс T632 прошёл успешно')

    def test_edit_passwd_for_ne_t633(self, edit_passwd_for_ne_fixture_t633):
        assert TEST_NODE["node_name"] in edit_passwd_for_ne_fixture_t633, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не найден'
        logger.warning(f'Сетевой элемент [ {TEST_NODE["node_name"]} ] найден')
        logger.info('Тест-кейс T633 прошёл успешно')

    def test_edit_ip_ne_t625(self, edit_ip_ne_fixture_t625):
        assert edit_ip_ne_fixture_t625 == CHANGE_IP, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не поменял свой IP'
        logger.warning(f'IP успешно изменен на {TEST_NODE["node_name"]} ')
        logger.info('Тест-кейс T625 прошёл успешно')

    def test_edit_port_for_ne_t631(self, edit_port_for_ne_fixture_t631):
        assert TEST_NODE["node_name"] in edit_port_for_ne_fixture_t631, f'Сетевой элемент [ {TEST_NODE["node_name"]} ] не найден'
        logger.warning(f'Сетевой элемент [ {TEST_NODE["node_name"]} ] найден')
        logger.info('Тест-кейс T631 прошёл успешно')

    def test_transition_to_ne_management_t634(self, transition_to_ne_management_t634):
        assert transition_to_ne_management_t634 == f'Management {NODE_NAME1}', \
            f'Вкладка Management {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Management NE для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T634 прошёл успешно')

    def test_transition_to_event_log_t637(self, transition_to_event_log_t637):
        assert transition_to_event_log_t637 == f'Events Node {NODE_NAME1}', f'Вкладка Events {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Events NE для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T637 прошёл успешно')

    def test_transition_to_software_upgrade_t635(self, transition_to_software_upgrade_fixture_t635):
        assert transition_to_software_upgrade_fixture_t635 == f'Node {NODE_NAME1} upgrade management', \
            f'Вкладка Node {NODE_NAME1} upgrade management не открыта'
        logger.warning(f'Вкладка Upgrade management для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T635 прошёл успешно')

    def test_transition_to_ASAP_profile_t1105(self, transition_to_asap_profile_fixture_t1105):
        assert transition_to_asap_profile_fixture_t1105 == f'ASAP Node {NODE_NAME1}', \
            f'Вкладка ASAP Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка ASAP NE для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1105 прошёл успешно')

    def test_transition_to_ASAP_exception_t1106(self, transition_to_asap_exception_fixture_t1106):
        assert transition_to_asap_exception_fixture_t1106 == f'ASAP Exceptions Node {NODE_NAME1}', \
            f'Вкладка ASAP Exceptions Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка ASAP Exceptions NE для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1106 прошёл успешно')

    def test_transition_to_oduxc_sncp_t1108(self, transition_to_oduxc_sncp_fixture_t1108):
        assert transition_to_oduxc_sncp_fixture_t1108 == f'ODU CrossConnections Node {NODE_NAME1}', \
            f'Вкладка ODU CrossConnections Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка ODU XC & SNCP для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1108 прошёл успешно')

    def test_transition_to_odu_protect_t1110(self, transition_to_odu_protect_t1110):
        assert transition_to_odu_protect_t1110 == f'ODU Protection Node {NODE_NAME1}', \
            f'Вкладка ODU Protection Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка ODU Protection для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1110 прошёл успешно')

    def test_transition_to_odu_mux_t1112(self, transition_to_odu_mux_t1112):
        assert f'ODU Multiplexing Node {NODE_NAME1}' in transition_to_odu_mux_t1112, \
            f'Вкладка ODU Multiplexing Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка ODU Multiplexing для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1112 прошёл успешно')

    def test_transition_to_vroadm_t1129(self, transition_to_vroadm_t1129):
        assert transition_to_vroadm_t1129 == f'VROADM Node {NODE_NAME1}', f'Вкладка VROADM Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка VROADM для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1129 прошёл успешно')

    def test_transition_to_alarm_log_t636(self, transition_to_alarm_log_t636):
        assert transition_to_alarm_log_t636 == f'Current Alarms Node {NODE_NAME1}', \
            f'Вкладка Current Alarms Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Current Alarms для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T636 прошёл успешно')

    def test_transition_to_nmc_connect_t1130(self, transition_to_nmc_connect_t1130):
        assert transition_to_nmc_connect_t1130 == f'NMC Connections Node {NODE_NAME1}', \
            f'Вкладка NMC Connections Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка NMC Connections для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1130 прошёл успешно')

    def test_transition_to_opt_protect_t1131(self, transition_to_opt_protect_t1131):
        assert transition_to_opt_protect_t1131 == f'Optical protection Node {NODE_NAME1}', \
            f'Вкладка Optical protection Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Optical protection для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1131 прошёл успешно')

    def test_transition_to_sens_tca_t1132(self, transition_to_sens_tca_fixture_t1132):
        assert transition_to_sens_tca_fixture_t1132 == f'Sensors & TCA Node {NODE_NAME1}', \
            f'Вкладка Sensors & TCA Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Sensors & TCA для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1132 прошёл успешно')

    def test_transition_to_chs_view_t1166(self, transition_to_chs_view_fixture_t1166):
        assert transition_to_chs_view_fixture_t1166 == f'Link Management {NODE_NAME1}', \
            f'Вкладка Link Management {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Link Management для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1166 прошёл успешно')

    def test_transition_to_2d_diagram_t1165(self, transition_to_2d_diagram_fixture_t1165):
        assert transition_to_2d_diagram_fixture_t1165 == f'Graph link Management {NODE_NAME1}', \
            f'Вкладка Graph link Management {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Graph link Management для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1165 прошёл успешно')

    def test_transition_to_gauge_stat_t1134(self, transition_to_gauge_stat_fixture_t1134):
        assert transition_to_gauge_stat_fixture_t1134 == f'Gauge Statistics Node {NODE_NAME1}', \
            f'Вкладка Gauge Statistics Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Gauge Statistics для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1134 прошёл успешно')

    def test_transition_to_conf_tree_t1167(self, transition_to_conf_tree_fixture_t1167):
        assert transition_to_conf_tree_fixture_t1167 == f'Config Tree {NODE_NAME1}', \
            f'Вкладка Config Tree {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка Config Tree для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1167 прошёл успешно')

    def test_transition_to_pm_stat_t1135(self, transition_to_pm_stat_fixture_t1135):
        assert transition_to_pm_stat_fixture_t1135 == f'PM Statistics Node {NODE_NAME1}', \
            f'Вкладка PM Statistics Node {NODE_NAME1} не открыта'
        logger.warning(f'Вкладка PM Statistics для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1135 прошёл успешно')


    def test_transition_to_lct_t1168(self, transition_to_lct_t1168):
        assert transition_to_lct_t1168 == "T8 АКСОН", f"LCT page of {NODE_NAME1} wasn't opened"
        logger.warning(f'Вкладка OPEN_LCT для сетевого элемента {NODE_NAME1} открыта')
        logger.info('Тест-кейс T1168 прошёл успешно')

    @pytest.mark.skip(reason="Not Implemented")
    def test_mass_edit_network_nodes_t1331(self):
    # def test_mass_edit_network_nodes_t1331(self, mass_edit_network_nodes_t1331):
        # fixture: mass_edit_network_nodes : not completed
        pass
        # Manual test didn't pass

    def test_mass_adm_lock_t1332(self, mass_adm_lock_t1332):
        for el in mass_adm_lock_t1332:
            assert el == "locked", f"NE {el} wasn't locked"
        logger.info('Тест-кейс T1332 прошёл успешно')

    def test_mass_adm_unlock_t1333(self, mass_adm_unlock_t1333):
        for el in mass_adm_unlock_t1333:
            assert el == "unlocked", f"NE {el} wasn't unlocked"
        logger.info('Тест-кейс T1333 прошёл успешно')

    def test_system_tab_ne_control_teardown(self, system_tab_ne_control_teardown):
        pass

    # def test_tmp(self, tmp1):
    #     pass

