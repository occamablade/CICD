from time import sleep

from Utilities.all import AdmStateEA, ConfigReset
from base.Atlas.atlas import SessionAPI
from confest import testing_slot, testing_devcls, IP_shassi

t = SessionAPI('s_ap', IP_shassi)
sleep(5)

if 'els' or 'evstc' or 'emstc' in testing_devcls:
    mode = t.get_param(AdmStateEA.format(testing_devcls, testing_slot, '1'))
    if mode == '2':
        pass
    elif mode == '1':
        t.set_param(AdmStateEA.format(testing_devcls, testing_slot, '1'), '2')
        sleep(5)
    else:
        t.set_param(AdmStateEA.format(testing_devcls, testing_slot, '1'), '1')
        sleep(5)
        t.set_param(AdmStateEA.format(testing_devcls, testing_slot, '1'), '2')
        sleep(5)
    mode = t.get_param(AdmStateEA.format(testing_devcls, testing_slot, '1'))
    t.set_param(ConfigReset.format(testing_devcls, testing_slot), '1')
    sleep(20)


def test_T130():
    assert t.get_param(AdmStateEA.format(testing_devcls, testing_slot, '1')) != mode


t.logout()
