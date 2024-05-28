from dataclasses import dataclass


@dataclass
class OpticsState:
    tx_opt_pwr: str = '/em/interfaces/interface[aid="{}"]/optics/tx-optical-power'
    cl_traffic_mode: str = '/em/interfaces/interface[aid="{}"]/optics/client-traffic-mode'
    coh_oper_mode: str = '/em/interfaces/interface[aid="{}"]/optics/coherent-operating-mode'
    tx_enable: str = '/em/interfaces/interface[aid="{}"]/tx-enable'
    adm_state: str = '/em/interfaces/interface[aid="{}"]/administrative-state'
    ch_state: str = '/em/interfaces/interface[aid="{}"]/wavelength/channel'
    min_thr_disp: str = '/em/interfaces/interface[aid="{}"]/optics/chromatic-dispersion-min-threshold'
    max_thr_disp: str = '/em/interfaces/interface[aid="{}"]/optics/chromatic-dispersion-max-threshold'


@dataclass
class OtuState:
    otu_rate: str = '/em/interfaces/interface[aid="{}"]/otu/rate'
    adm_state: str = '/em/interfaces/interface[aid="{}"]/administrative-state'


@dataclass
class OduState:
    odu_rate: str = '/em/interfaces/interface[aid="{}"]/odu/rate'
    adm_state: str = '/em/interfaces/interface[aid="{}"]/administrative-state'
    odu_conn_op_st: str = "/em/odu-connections/connection[contains(source-aid,'{}')]/operational-state"


@dataclass
class PortState:
    """
    aid begins with 'XPC or XPL'
    """
    oper_state: str = '/em/ports/port[aid="{}"]/operational-state'
    adm_state: str = '/em/ports/port[aid="{}"]/administrative-state'


@dataclass
class SlotState:
    oper_state: str = '/em/slots/slot[aid="{}"]/operational-state'
    adm_state: str = '/em/slots/slot[aid="{}"]/administrative-state'
    stab_mode: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/stabilization-mode'
    gain_value: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/gain'
    enable_gain_limit: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/enable-gain-limit'
    output_pwr_sig_limit: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/output-power-signal-limit'
    apr_enable: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/apr/enable'
    asm_auto_tuning: str = '/em/circuit-packs/circuit-pack[aid="{}"]/ea/auto-stabilization/enable-auto-tuning'


@dataclass
class Info:
    module_prt_number: str = '/em/circuit-packs/circuit-pack/info/common/model'
    serial_number: str = '/em/circuit-packs/circuit-pack/info/common/serial-number'
    vendor: str = '/em/circuit-packs/circuit-pack/info/common/vendor'
    software_rev: str = '/em/circuit-packs/circuit-pack/info/common/software-revision'


@dataclass
class RoadmConnections:
    nmc_connection: str = "/em/nmc-connections/connection[contains(source-aid,'{}')]"
    add_drop: str = "/em/add-drops/add-drop[contains(add-physical-port,'{}')]"
    degrees: str = "/em/degrees/degree[contains(aid,'{}')]"

