# ---------------------------------
# Путь к авариям/дефектам (CNE)
# ---------------------------------
FM = 'http://192.168.{}:81/restconf/data/fm/conditions'

# ---------------------------------
# Creds node
# ---------------------------------
USER = 'root'
PASSW = 'rack~flvbybcnhfnjh~cu2'
ROLE = 's_ap'

# ---------------------------------
# Ссылки на репозиторий с прошивками
# ---------------------------------
CU_REPO_URL = 'http://192.168.29.110:8000/api/getPackages/'
BOARD_REPO_URL = 'http://192.168.29.110:8000/api/getProd/'
BOARD_URI = 'http://192.168.29.110:8000/api/getFile/slashfirmwaresslash'
CU_URI = 'http://192.168.29.110:8000/api/getFile/slash'
DOWNLOAD_PATH_WTH_VERSION = 'http://192.168.29.110:8000/api/getFile?path=firmwares%2F{}%2F{}%2F{}%2F{}&type=file&directoryType=getProd'
DOWNLOAD_PATH_WTHT_VERSION = 'http://192.168.29.110:8000/api/getFile?path=firmwares%2F{}%2F{}%2F{}&type=file&directoryType=getProd'
DOWNLOAD_PATH_FOR_CU_FIRMWARE = 'http://192.168.29.110:8000/api/getFile?path={}%2F{}%2F{}&type=file&directoryType=getPackages'

# ---------------------------------
# Кортежи с значениями для LLF теста
# ---------------------------------
# DURATION = tuple(range(500, 1001, 4))
# PERIOD = tuple(range(3000, 20001, 136))
# DELAY = tuple(range(0, 1001, 8))
DURATION = tuple(range(500, 511))
PERIOD = tuple(range(3000, 20401, 34))
DELAY = tuple(range(0, 1021, 2))

# ---------------------------------
# Переменные для счётчиков
# ---------------------------------
WAIT_COUNT = 10
WAIT = 300
WAIT_REBOOT = 180

# ---------------------------------
# Переменные для слотовых устройств
# ---------------------------------
FREQ_SET = 'mjm3_5_ATP1Ln1FreqSet'
FREQ_GET = 'mjm3_5_ATP1Ln1Frq'

PORT_ST_LN = '{}_{}_ATP1Ln{}PortState'
PORT_ST_CL = '{}_{}_ATP1Cl{}PortState'
TX_ST_LN = '{}_{}_ATP1Ln{}TxEnable'
TX_ST_CL = '{}_{}_ATP1Cl{}TxEnable'
LB_ST = '{}_{}_ATP1Ln{}LBModeSet'
# PORT_ST = 'mjc2_4_ATP1{}PortState'
# TX_ST = 'mjc2_4_ATP1{}TxEnable'
# LB_ST = 'mjc2_4_ATP1{}LBModeSet'
CFP1, CFP2 = 'mjm3_5_CFP1PtNumber', 'mjm3_5_CFP2PtNumber'
# GET_SWNUMBER = 'mjb6_2_SwNumber'
ConfigReset = '{}_{}_Dev.ConfigReset'

Default = '{}_{}_SetDefaultSettings'
VoaPortState = '{}_{}_VOAAll.Port.State'
VOAAllAttSet = '{}_{}_VOAAll.Att.Set'

VOAMin = '{}_{}_VOA{}.Att.SetHMin'
VOAMax = '{}_{}_VOA{}.Att.SetHMax'
VOAAtt = '{}_{}_VOA{}.Att.Set'

pId = '{}_{}_pId'
SlotNEnable = '{}_{}_Slot{}Enable'
# ---------------------------------
# Переменные для EA
# ---------------------------------
AdmStateEA = '{}_{}_EA{}.AdmState.Set'
AmplifierEA = '{}_{}_EA{}.Amplifier.Enable'
GainEA = '{}_{}_EA{}.Gain'
GainSetEA = '{}_{}_EA{}.Gain.Set'
PowerSigSetEA = '{}_{}_EA{}.Out.PowerSig.Set'
PowerSigEA = '{}_{}_EA{}.Out.PowerSig'
OutPowerEA = '{}_{}_EA{}.Out.Power'
StModeChoises = {'0': 'Выкл',
                 '1': 'Gain',
                 '2': 'Pout',
                 '3': 'ASM'}
StModeEA = '{}_{}_EA{}.StMode.Set'
StModeSet = '{}_{}_EA{}St1StModeSet'
EASt1GainWMax = '{}_{}_EA{}St1GainWMax'
EASt1GainWMin = '{}_{}_EA{}St1GainWMin'
EAGainWMax = '{}_{}_EA{}.GainWMax'
EAGainWMin = '{}_{}_EA{}.GainWMin'
EAOutPowerSigSetHMax = '{}_{}_EA{}.Out.PowerSig.SetHMax'
EAOutPowerSigSetHMin = '{}_{}_EA{}.Out.PowerSig.SetHMin'
EAStPoutFWMax = '{}_{}_EA{}St1PoutFWMax'
EAStPoutFWMin = '{}_{}_EA{}St1PoutFWMin'
EASt1GainSet = '{}_{}_EA{}St1GainSet'
EASt1PoutSet = '{}_{}_EA{}St1PoutSet'
EAOutPowerSig = '{}_{}_EA{}.Out.PowerSig'
# ---------------------------------
# Переменные для ROADM
# ---------------------------------
ChAll = '{}_{}_WSS.ChAll.State.Set'
WssAtt = '{}_{}_WSS.ChAll.VOA.Att.Set'
# ---------------------------------
# Переменные для VOA
# ---------------------------------
VOAAttSetHMax = '{}_{}_VOA{}.Att.SetHMax'
VOAAttSetHMin = '{}_{}_VOA{}.Att.SetHMin'
ChAttSetHMax = '{}_{}_Ch{}.Att.SetHMax'
ChAttSetHMin = '{}_{}_Ch{}.Att.SetHMin'
VOAPortAttWMax = '{}_{}_VOAPort{}AttWMax'
VOAPortAttWMin = '{}_{}_VOAPort{}AttWMin'
VOAOutPortState = '{}_{}_VOA{}Out.Port.State'
VOAPortAttSet = '{}_{}_VOAPort{}AttSet'
VOAAttSet = '{}_{}_VOA{}.Att.Set'
ChAttSet = '{}_{}_Ch{}.Att.Set'
VOAAdmState = '{}_{}_VOA{}.AdmState.Set'
VoaChAdmStateSet = '{}_{}_Ch{}.AdmState.Set'
# ---------------------------------
# Переменные для MS
# ---------------------------------
AdmStateLn = '{}_{}_Ln{}.AdmState.Set'
AdmStateCl = '{}_{}_Cl{}.AdmState.Set'
TxLn = '{}_{}_Ln{}.Tx.En'
TxCl = '{}_{}_Cl{}.Tx.En'
TypeTrafficCl = '{}_{}_Cl{}.DR.Set'
LinkCl = '{}_{}_Cl{}.Link.W.Set'
LnNAdmStateSet = '{}_{}_Ln{}.AdmState.Set'
ClNAdmStateSet = '{}_{}_Cl{}.AdmState.Set'
LnNTxEn = '{}_{}_Ln{}.Tx.En'
ClNTxEn = '{}_{}_Cl{}.Tx.En'
ClNDRSet = '{}_{}_Cl{}.DR.Set'
ClNLinkWSet = '{}_{}_Cl{}.Link.W.Set'
LnAllAdmStateSet = '{}_{}_LnAll.AdmState.Set'
ClAllAdmStateSet = '{}_{}_ClAll.AdmState.Set'
LnAllTxEn = '{}_{}_LnAll.Tx.En'
ClAllTxEn = '{}_{}_ClAll.Tx.En'
ClAllDRSet = '{}_{}_ClAll.DR.Set'
# ---------------------------------
# IP для шасси
# ---------------------------------
CHS192, CHS194 = '192.168.31.192', '192.168.31.194'

# ---------------------------------
# Переменные для EXFO
# ---------------------------------
EXFO_IP, MODULE = '192.168.31.182', 4

# ---------------------------------
# Путь для обновления слотовых устройств (Atlas)
# ---------------------------------
UPLOAD = 'http://192.168.{}/upload.php'

# ---------------------------------
# Переменные для обновления слотовых устройств (Atlas)
# ---------------------------------
FW_POSTFIX = '*.s19'
UPDATABLE_SLOT = '5'

# ---------------------------------
# Переменные для перезагрузки слотовых устройств (Atlas)
# ---------------------------------
REBOOT_SLOT = 'dnepr3_10_Slot6Restart'
REBOOT_VAL = '1'

# ---------------------------------
# Переменные для создания backup`a
# ---------------------------------
BACKUP_SLOT = '6'
BACKUP_DEV_CLS = 'mjstc3'

# ---------------------------------
# Заголовок для csv
# ---------------------------------
TITLE = ['Set Freq', 'Get Freq', 'Delta', 'Verdict']

# ---------------------------------
# Переменные для работы с API Atlas
# ---------------------------------
ADMN = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="Authorize"><LOGIN>Admin</LOGIN><PASSWORD>cradmin</PASSWORD></QUERY>'
SUP_USER = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="Authorize"><LOGIN>SuperUser</LOGIN><PASSWORD>cegth.pthcrb6</PASSWORD></QUERY>'
DISCONNECT = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="Logout"><SESSION_ID>{}</SESSION_ID></QUERY>'
GET_P = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="GetParams"><SESSION_ID>{}</SESSION_ID><UID>{}</UID></QUERY>'
SET_P = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="SetParam"><SESSION_ID>{}</SESSION_ID><PARAM UID="%s"><VALUE>%s</VALUE></PARAM></QUERY>'
GET_PARAM_BACKUP_DATA = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="GetParamBackupData"><SESSION_ID>{}</SESSION_ID><DEVICE><SLOT>{}</SLOT><DEVICE_CLASS>{}</DEVICE_CLASS></DEVICE></QUERY>'
BACKUP = '<?xml version="1.0" encoding="utf-8"?><QUERY Action="BackupParams"><SESSION_ID>{}</SESSION_ID><DEVICE><SLOT>{}</SLOT><DEVICE_CLASS>{}</DEVICE_CLASS></DEVICE></QUERY>'

# ---------------------------------
# Виды трафика на ладоге
# ---------------------------------
traffic_choices = {'1': 'STM-1',
                   '2': 'STM-4',
                   '3': 'STM-16',
                   '4': 'STM-64',
                   '11': '2GFC',
                   '21': 'OTU1',
                   '25': 'OTU2',
                   '26': 'OTU2e',
                   '40': '1GE',
                   '41': '10GE',
                   '255': '--'}

main_source = {'524288': 'Ln1.ODU0.TS1',
               '524289': 'Ln1.ODU0.TS2',
               '524290': 'Ln1.ODU0.TS3',
               '524291': 'Ln1.ODU0.TS4',
               '524292': 'Ln1.ODU0.TS5',
               '524293': 'Ln1.ODU0.TS6',
               '524294': 'Ln1.ODU0.TS7',
               '524295': 'Ln1.ODU0.TS8',
               '524544': 'Ln1.ODU1.TS1',
               '524546': 'Ln1.ODU1.TS2',
               '524548': 'Ln1.ODU1.TS3',
               '524550': 'Ln1.ODU1.TS4',
               '589824': 'Ln2.ODU0.TS1',
               '589825': 'Ln2.ODU0.TS2',
               '589826': 'Ln2.ODU0.TS3',
               '589827': 'Ln2.ODU0.TS4',
               '589828': 'Ln2.ODU0.TS5',
               '589829': 'Ln2.ODU0.TS6',
               '589830': 'Ln2.ODU0.TS7',
               '589831': 'Ln2.ODU0.TS8',
               '590080': 'Ln2.ODU1.TS1',
               '590082': 'Ln2.ODU1.TS2',
               '590084': 'Ln2.ODU1.TS3',
               '590086': 'Ln2.ODU1.TS4',
               '656128': 'Ln1.ODU2',
               '721408': 'Ln2.ODU2e',
               '721664': 'Ln2.ODU2',
               '787200': 'Ln3.ODU2',
               '852736': 'Ln4.ODU2',
               '918016': 'Ln5.ODU2e',
               '918272': 'Ln5.ODU2',
               '983808': 'Ln6.ODU2',
               '1049088': 'Ln7.ODU2e',
               '1049344': 'Ln7.ODU2',
               '1114880': 'Ln8.ODU2',
               '1180416': 'Ln9.ODU2',
               '1245696': 'Ln10.ODU2e',
               '1245952': 'Ln10.ODU2',
               '16252928': 'ALARM',
               '16318464': 'OPEN',
               '16384000': 'LOCK'}

force_ODU2 = {'768': 'Cl1.ODU2',
              '66304': 'Cl2.ODU2',
              '131840': 'Cl3.ODU2',
              '197376': 'Cl4.ODU2',
              '262912': 'Ln1.ODU2',
              '328448': 'Ln2.ODU2',
              '393984': 'Ln3.ODU2',
              '459520': 'Ln4.ODU2'
              }

traffic_TQ = {'4': 'STM-64',
              '41': '10GE(6.2)',
              '42': '10GE(7.3)',
              }
StMode = {'0': 'Выкл',
          '1': 'Gain',
          '2': 'Pout',
          '3': 'ASM'}
# ---------------------------------
# Виды трафика на BERTe
# ---------------------------------
stm1 = b'TermStm1oAu3Vc3Bert'
stm4 = b'TermStm4Au44cVc44cBert'
stm16 = b'TermStm16Au416cVc416cBert'
stm64 = b'TermStm64Au3Vc3Bert'
GE_10 = b'TermEth10GL2Traffic'
Ge_WAN = b'TermStm64Au464cVc464cEthL2Traffic'
GE = b'TermEth1GL2Traffic'
FE = b'TermEth100ML2Traffic'
ETH = b'TermEth10ML2Traffic'
OTU_2 = b'TermOtn107Odu2Bert'
OTU_2e = b'TermOtn111Odu2Bert'
OTU_1 = b'TermOtn27Odu1Bert'
OTU_1e = b'TermOtn1105Odu2Bert'
FC_8 = b'TermFc8GL2Traffic'
FC_4 = b'TermFc4GL2Traffic'
FC_2 = b'TermFc2GL2Traffic'
FC_1 = b'TermFc1GL2Traffic'
# ---------------------------------
# Виды ошибок в атласе
# ---------------------------------
error_04 = "04 - Значение выходит за пределы порогов"
error_06 = "06 - Строка с параметрами слишком длинная (4294967294)"
error_07 = "07 - Значение нарушает монотонность порогов"
error_42 = "Ошибка во входных данных: указанное значение не соответствует типу параметра"
# Переменные для работы с NMS
# ---------------------------------
LINE_PORT = 'XPL-1-1-{}-0-LINE1'
LINE_OPT = 'OPT-1-1-{}-0-LINE1'
LINE_ODU = 'ODU-1-1-{}-0-LINE1'
LINE_OTU = 'OTU-1-1-{}-0-LINE1'
URL_NMS = 'http://192.168.180.104:8888/api'
URL_LOGIN_NMS = 'http://192.168.180.104:8888/login'
# URL_LOGIN_NMS = 'http://192.168.30.175/login'
LOGIN_NMS = 'brauer'
PASSWD_NMS = 'XDR%4esz'
TEST_LOGIN_NMS = 'testing_dep'
TEST_PASSWD_NMS = 'VGY&8uhb'
PPM = 'PPM-1-1-9-0-LINE1'

IP = '192.168.31.50'
CHANGE_IP = '192.168.31.49'
NODE_ID = 'NE_50_TEST'
NODE_NAME = 'NE_50_TEST'
ADM_ST = 'unlocked'
PORT = '830'
CHANGE_PORT = '831'
USER_FOR_NE = 'nms'
PASSWD_FOR_NE = 'nms'
NODE_NAME1 = 'shass_157'

TEST_NODE = {'node_id': 'NE_50_TEST', 'node_name': 'NE_50_TEST', 'node_ip': '192.168.31.50',
             'node_domain': 'OT', 'node_port': 830, 'node_user': 'nms', 'node_passw': 'nms'}

NODE_LIST_FOR_MASS_OPS = ['shass_155', 'shass_156', 'shass_157', ]

PING_DATA = {'node_name': 'shass_157', 'target_ip': '192.168.31.157',
             'source': 'ncw_177', 'packet_len': 56, 'quantity': 3,
             'interval': 1000, 'timeout': 1}
TRACEROUTE_DATA = {'node_name': 'shass_155', 'target_ip': '192.168.31.155',
                   'source': 'ncw_177', 'timeout': 1, 'max_ttl': 30}
IP_TUNNEL_DATA1 = {'node1_name': 'shass_155', 'tunnel_name': 'iptun3',
                   'local_ip': '192.168.31.155', 'remote_ip': '192.168.31.156',
                   'role': 'OSC', 'description': 'IP Tunnel 155 > 156'}
IP_TUNNEL_DATA2 = {'node1_name': 'shass_155', 'tunnel_name': 'iptun3',
                   'local_ip': '192.168.31.156', 'remote_ip': '192.168.31.157',
                   'role': 'OSC', 'description': 'IP Tunnel 156 > 157'}

EXCLUDED_DEVICES = ['SLOT PS1', 'SLOT PS2', 'SLOT FU', 'SLOT CU1', 'SLOT CU0', 'SLOT 3', 'SLOT 1']
TESTING_SLOT_NAME = ['SLOT 2 MS-D100EC2-DT10']
