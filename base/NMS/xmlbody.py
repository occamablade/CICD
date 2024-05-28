from xml.etree import ElementTree as ET


class XmlData:

    @staticmethod
    def set_attenuation(value: str, aid: str) -> str:
        """
        Создаёт строку для изменения аттенюации
        :param value: значение аттенюации
        :param aid: аид порта
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        prts = ET.SubElement(cfg, 'ports')
        prt = ET.SubElement(prts, 'port')
        ET.SubElement(prt, 'aid').text = aid
        voa = ET.SubElement(prt, 'voa')
        ET.SubElement(voa, 'target-attenuation').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_adm_st(value: str, aid: str) -> str:
        """
        Создание строки для изменения административного состояния порта
        :param value: locked или unlocked
        :param aid: аид порта
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        prts = ET.SubElement(cfg, 'ports')
        prt = ET.SubElement(prts, 'port')
        ET.SubElement(prt, 'administrative-state').text = value
        ET.SubElement(prt, 'aid').text = aid

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_adm_st_interface(value: str, aid: str) -> str:
        """
        Создание строки для изменения административного состояния интерфейса
        :param value: locked или unlocked
        :param aid: аид интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        prts = ET.SubElement(cfg, 'interfaces')
        prt = ET.SubElement(prts, 'interface')
        ET.SubElement(prt, 'administrative-state').text = value
        ET.SubElement(prt, 'aid').text = aid

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_tx_enable(value: str, aid: str) -> str:
        """
        Создание строки для вкл/выкл передатчика
        :param value: true или false
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'tx-enable').text = value
        ET.SubElement(it, 'aid').text = aid

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_tx_power(value: str, aid: str) -> str:
        """
        Создание строки для изменения вых мощности
        :param value: значение выходной мощности
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        ET.SubElement(opt, 'tx-optical-power').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_als_enable(value: str, aid: str) -> str:
        """
        Создание строки для вкл/выкл ALS
        :param value: true или false
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        ET.SubElement(opt, 'als-enable').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def select_coherent_opt_mode(value: str, aid: str) -> str:
        """
        Создание строки для когерентного режима
        :param value: necemot:ndiff-16qam-ofec-200g, necemot:ndiff-8qam-ofec-200g и т.д.
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        coh = ET.SubElement(opt, 'coherent-operating-mode')
        coh.set('xmlns:necemot', 'urn:nec:params:xml:ns:yang:nec-em-optical-types')
        coh.text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_max_thr_dispersion(value: str, aid: str) -> str:
        """
        Создание строки для изменения максимальной дисперсии
        :param value: значение дисперсии
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        max_disp = ET.SubElement(opt, 'chromatic-dispersion-max-threshold')
        max_disp.text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_min_thr_dispersion(value: str, aid: str) -> str:
        """
        Создание строки для изменения минимальной дисперсии
        :param value: значение дисперсии
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        min_disp = ET.SubElement(opt, 'chromatic-dispersion-min-threshold')
        min_disp.text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def select_wavelength_via_ch(value: str, aid: str) -> str:
        """
        Создание строки для изменения длины волны через номер канала
        :param value: номер канала
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'wavelength')
        ch = ET.SubElement(opt, 'channel')
        ch.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-nmc')
        ch.text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def select_wavelength_grid(value: str, aid: str) -> str:
        """
        Создание строки для выбора частотной сетки
        :param value:
        :param aid: аид оптического интерфейса
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'wavelength')
        ch = ET.SubElement(opt, 'grid')
        ch.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-nmc')
        ch.text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def set_cl_mapping_and_tr_mode(aid: str, mapping: str, mode: str) -> str:
        """
        Создание строки для выбора типа трафика и типа упаковки на клиенте
        :param aid: аид клиентского интерфейса
        :param mapping: например GFP-F-7.3
        :param mode: например ETH-10G-LAN
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        opt = ET.SubElement(it, 'optics')
        cl_tr = ET.SubElement(opt, 'client-traffic-mode')
        mod = ET.SubElement(cl_tr, 'mode')
        mod.set('xmlns:nectrft', 'urn:nec:params:xml:ns:yang:nec-common-traffic-types')
        mod.text = f'nectrft:{mode}'
        mapp = ET.SubElement(cl_tr, 'mapping')
        mapp.set('xmlns:necotnt', 'urn:nec:params:xml:ns:yang:nec-common-otn-types')
        mapp.text = f'necotnt:{mapping}'

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def create_odu_protect(
            aid_wrk: str,
            aid_prt: str,
            sncp_type: str,
            directionality: str = 'bidirectional',
            revert_mode: str = 'non-revertive') -> str:
        """
        Создание строки для создания группы защиты
        :param aid_wrk: аид основного интерфейса, например ODU-1-1-9-0-LINE1-TP1
        :param aid_prt: аид резервного интерфейса, например ODU-1-1-9-0-LINE2-TP1
        :param sncp_type: snc-i или snc-n
        :param directionality: bidirectional или unidirectional
        :param revert_mode: revertive или non-revertive
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        pg = ET.SubElement(cfg, 'pg')
        pg.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-pg')
        ipg = ET.SubElement(pg, 'interface-protection-groups')
        group = ET.SubElement(ipg, 'group')
        ET.SubElement(group, 'working-interface-aid').text = aid_wrk
        ET.SubElement(group, 'protecting-interface-aid').text = aid_prt
        ET.SubElement(group, 'sncp-type').text = sncp_type
        ET.SubElement(group, 'directionality').text = directionality
        ET.SubElement(group, 'revertive-mode').text = revert_mode
        ET.SubElement(group, 'administrative-state').text = 'unlocked'

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def setup_mux_hs(aid: str, num: int) -> str:
        """
        Создание строки для создания mux на высокоскоростных платах
        :param aid: Аид для HO ODU, например ODU-1-1-9-0-LINE1
        :param num: номер трибутарного порта
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        its = ET.SubElement(cfg, 'interfaces')
        it = ET.SubElement(its, 'interface')
        ET.SubElement(it, 'aid').text = aid
        odu = ET.SubElement(it, 'odu')
        mux = ET.SubElement(odu, 'mux')
        ET.SubElement(mux, 'tsg').text = 'odu0'
        tp = ET.SubElement(mux, 'tributary-ports')
        p1 = ET.SubElement(tp, 'port')
        ET.SubElement(p1, 'number').text = str(num)
        # ET.SubElement(p1, 'ts-mask').text = '8'
        ET.SubElement(p1, 'ts-amount').text = '8'

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def create_odu_connection(
            src_aid: str,
            dst_aid: str,
            adm_state: str = 'unlocked',
            directionality: str = 'bidirectional') -> str:
        """
        Создание строки для создания кросс-коннекта
        :param src_aid: аид источника, это клиенткий ODU, например ODU-1-1-9-0-C1
        :param dst_aid: аид назначения, это аид трибутарного порта, например ODU-1-1-9-0-LINE1-TP1
        :param adm_state: locked или unlocked
        :param directionality: bidirectional или unidirectional
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        odu_con = ET.SubElement(cfg, 'odu-connections')
        odu_con.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-connections')
        con = ET.SubElement(odu_con, 'connection')
        ET.SubElement(con, 'source-aid').text = src_aid
        ET.SubElement(con, 'destination-aid').text = dst_aid
        ET.SubElement(con, 'administrative-state').text = adm_state
        ET.SubElement(con, 'directionality').text = directionality

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def setup_mux_ls():
        # TODO сделать метод для создания ТР на низкоскоростных платах
        pass

    @staticmethod
    def change_stabilization_mode(aid: str, mode: str) -> str:
        """
        Создание строки для выбора режима стабилизации на усилителях
        :param aid: аид, например EA-1-1-7-1
        :param mode: gain, auto-stabilization, output-power
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        cps = ET.SubElement(cfg, 'circuit-packs')
        cp = ET.SubElement(cps, 'circuit-pack')
        ET.SubElement(cp, 'aid').text = aid
        ea = ET.SubElement(cp, 'ea')
        ea.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-oamp')
        ET.SubElement(ea, 'stabilization-mode').text = mode

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_gain_value(aid: str, value: str) -> str:
        """
        Создание строки для изменения gain
        :param aid: аид, например EA-1-1-7-1
        :param value: значение
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        cps = ET.SubElement(cfg, 'circuit-packs')
        cp = ET.SubElement(cps, 'circuit-pack')
        ET.SubElement(cp, 'aid').text = aid
        ea = ET.SubElement(cp, 'ea')
        ea.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-oamp')
        ET.SubElement(ea, 'gain').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_enable_gain_limit(aid: str, value: str) -> str:
        """
        Создание строки для вкл/выкл gain limit
        :param aid: аид, например EA-1-1-7-1
        :param value: 'true' или 'false'
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        cps = ET.SubElement(cfg, 'circuit-packs')
        cp = ET.SubElement(cps, 'circuit-pack')
        ET.SubElement(cp, 'aid').text = aid
        ea = ET.SubElement(cp, 'ea')
        ea.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-oamp')
        ET.SubElement(ea, 'enable-gain-limit').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_output_pwr_sig_limit(aid: str, value: str) -> str:
        """
        Создание строки для изменения лимита
        :param aid: аид, например EA-1-1-7-1
        :param value:
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        cps = ET.SubElement(cfg, 'circuit-packs')
        cp = ET.SubElement(cps, 'circuit-pack')
        ET.SubElement(cp, 'aid').text = aid
        ea = ET.SubElement(cp, 'ea')
        ea.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-oamp')
        ET.SubElement(ea, 'output-power-signal-limit').text = value

        return ET.tostring(xml).decode('UTF-8')

    @staticmethod
    def change_apr_enable(aid: str, value: str) -> str:
        """
        Создание строки для вкл/выкл APR
        :param aid: аид, например EA-1-1-7-1
        :param value: 'true' или 'false'
        :return:
        """
        xml = ET.Element('config')
        cfg = ET.SubElement(xml, 'em-config')
        cps = ET.SubElement(cfg, 'circuit-packs')
        cp = ET.SubElement(cps, 'circuit-pack')
        ET.SubElement(cp, 'aid').text = aid
        ea = ET.SubElement(cp, 'ea')
        ea.set('xmlns', 'urn:nec:params:xml:ns:yang:nec-em-oamp')
        apr = ET.SubElement(ea, 'apr')
        ET.SubElement(apr, 'enable').text = value

        return ET.tostring(xml).decode('UTF-8')
