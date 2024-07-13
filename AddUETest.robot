*** Settings ***
Library    JSONLibrary
Library    sdk/src/modules/RFsimUEManager.py    WITH NAME    RFsim
Library    sdk/src/main/init_handler.py    WITH NAME    Handler
Library    scripts/AddUETest.py     WITH NAME    AddUETest


*** Variables ***
${DOCKER_YAML_PATH}   ../5g_rfsimulator/docker-compose.yaml
${nb_of_users}    ${5}
${one}    ${1}


*** Test Cases ***
Initial Add and Remove UE
    [Documentation]    Add 1 UEs and remove 1 to prepare for the main test
    RFsim.Add UEs    ${one}  
    Sleep    30s
    RFsim.Remove UEs    ${one}

Start Handler
    [Documentation]    Start the handler and wait for it to initialize
    Handler.start_handler
    Sleep    5s

Add Multiple UEs
    [Documentation]    Add multiple UEs sequentially
    FOR    ${user}    IN RANGE    ${nb_of_users}
         RFsim.Add UEs    ${1}
         Sleep    15s
    END

Check IMSI Match
    [Documentation]    Check if IMSIs in Docker YAML match those in handler
    AddUETest.check_imsi_match    ${DOCKER_YAML_PATH}    ${nb_of_users}

Final Remove UEs
    [Documentation]    Remove all UEs added during the test
    FOR    ${user}    IN RANGE    ${nb_of_users}
         RFsim.Remove UEs    ${1}
    END
    Sleep    3s
    Handler.stop_handler
    