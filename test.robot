*** Settings ***
Library           OperatingSystem
Library    scripts/AddUETest.py     WITH NAME    AddUETest

*** Test Cases ***
Check SMF Notifications
    [Tags]    AMF  SMF  UPF
    ${logs} =     Run   docker logs rfsim5g-oai-smf | sed -n '/SMF CONTEXT:/,/^[[:space:]]*$/p' 
    Log    ${logs}    level=INFO
    AddUETest.check_smf_logs_and_callback_notification    '${logs}'
