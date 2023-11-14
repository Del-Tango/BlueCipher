#!/bin/bash
#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# BlueCipher Build WizZard

declare -a DEPENDENCIES
declare -a BUILD_DIRS

# Hot parameters

MODE='BUILD' # (SETUP | TEST | BUILD | CLEANUP)
BUILD='off'
INSTALL='off'
PUBLISH='off'
YES='off'

# Cold parameters

SCRIPT_NAME='Build WizZard'
VERSION='SpeedBall'
VERSION_NO='1.0'
DEPENDENCIES=('python3' 'python3-pip', 'python3-venv')
DISTRIBUTION_DIR='./dist'
VENV_DIR='./.venv'
CONF_DIR='./conf'
REQUIREMENTS_FILE='./requirements.txt'
PACKAGE_NAME='bluecipher'
BUILD_DIRS=('_build/' "${DISTRIBUTION_DIR}" "${PACKAGE_NAME}.egg-info/" "${PACKAGE_NAME}")
PARENT_DIR="$(basename "$(dirname "$(realpath ./setup.py)")")"

function display_usage() {
  cat <<EOF
  _____________________________________________________________________________

    *                          *  ${SCRIPT_NAME}  *                          *
  ___________________________________________________v${VERSION_NO}${VERSION}_____________
              Excellent Regards, the Alveare Solutions #!/Society -x

    [ Usage ]: ~$ $0 (BUILD | INSTALL | PUBLISH)

        -h  | --help                 Display this message.

        -s  | --setup                Install build dependencies.

        -t  | --test                 Run autotesters.

        -c  | --cleanup              Cleanup project directory. Removes directories
            |                        created during the build process, removes
            |                        compiled python __pycache__'s, the mypy cahe
            |                        and overwrites all log files with a timestamp.

        -y  | --yes                  Skips all user interactive prompts.

    [ Example ]: Install dependencies -

        ~$ sudo $0 --setup

    [ Example ]: Run autotesters and check type hints in source files -

        ~$ $0 --test --cleanup -y

    [ Example ]: Build the source and binary distributions -

        ~$ $0
        ~$ $0 BUILD

        [ NOTE ]: Build is set as the default, so it doesn't need to be
            specified unless this build wizzard script is modified.

    [ Example ]: Build distributions and install source -
        ~$ $0 BUILD INSTALL

    [ Example ]: Time saver -
        ~$ $0 --cleanup -y --setup --test BUILD INSTALL; $PACKAGE_NAME
EOF
}

# ACTIONS

function setup() {
    echo "[ SETUP ]: Dependencies..."
    local FAILURES=0
    for package in "${DEPENDENCIES[@]}"; do
        if ! apt-get install "${package}" -y $?; then
            echo "[ NOK ]: Failed to install ${package}"
            local FAILURES=$((FAILURES + 1))
        fi
    done
    if [ ! -d "${VENV_DIR}" ] && ! python3 -m venv ${VENV_DIR}; then
        echo "[ NOK ]: Failed to create virtual environment in (${VENV_DIR})"
        local FAILURES=$((FAILURES + 1))
    fi
    if ! ${VENV_DIR}/bin/python3 -m pip install -r "${REQUIREMENTS_FILE}"; then
        echo "[ NOK ]: Failed to install requirements file ${REQUIREMENTS_FILE}"
        local FAILURES=$((FAILURES + 1))
    fi
    return $FAILURES
}

function build() {
    echo "[ BUILD ]: Source and binary distributions..."
    local FAILURES=0
    if ! mkdir ${PACKAGE_NAME}; then
        rm -rf ${PACKAGE_NAME}
        mkdir ${PACKAGE_NAME}
    fi
    if ! cp -r ./* ${PACKAGE_NAME} 2>/dev/null; then
        echo "[ NOK ]: Could not create consumable artifact directory!"
    fi
    if ! ${VENV_DIR}/bin/python3 setup.py sdist; then
        local FAILURES=$((FAILURES + 1))
        echo "[ NOK ]: Could not build project source distribution!"
    fi
    if [ $FAILURES -ne 0 ]; then
        echo "[ NOK ]: Consumable artifact build terminated with (${FAILURES}) failures!"
    else
        echo "[ OK ]: Consumable artifact build!"
    fi
    return $FAILURES
}

function install() {
    echo "[ INSTALL ]: Source distribution archive..."
    if ! ${VENV_DIR}/bin/python3 -m pip install $(find ./dist -type f -name '*.tar.gz'); then
        echo "[ NOK ]: Failed to install source distribution package!"
        return $?
    else
        echo "[ OK ]: Installed source distribution package!"
    fi
    return 0
}

function cleanup() {
    echo "[ CLEANING ]: Project directory for Ricks..."
    local FAILURES=0
    echo "[ ... ]: Compiled Python __pycache__ directories"
    if ! rm -rf $(find . -type d -name '__pycache__'); then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Python build directories"
    if ! rm -rf "${BUILD_DIRS[@]}"; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Package directory"
    rm -rf "${PACKAGE_NAME}"
    if ! rm -rf "${PACKAGE_NAME}"; then
        local FAILURES=$((FAILURES + 1))
    fi
    echo "[ ... ]: Python package"
    if [[ "${YES}" == 'on' ]]; then
        ${VENV_DIR}/bin/python3 -m pip uninstall "${PACKAGE_NAME}" -y
    else
        ${VENV_DIR}/bin/python3 -m pip uninstall "${PACKAGE_NAME}"
    fi
    if [ $? -ne 0 ]; then
        local FAILURES=$((FAILURES + 1))
    fi
    return $FAILURES
}

# INIT

function init_build_wizzard() {
    local EXIT_CODE=0
    if [[ "$BUILD" == 'on' ]]; then
        build
        EXIT_CODE=$((EXIT_CODE + $?))
    fi
    if [[ "$INSTALL" == 'on' ]]; then
        install
        EXIT_CODE=$((EXIT_CODE + $?))
    fi
    return $EXIT_CODE
}

# MISCELLANEOUS

EXIT_CODE=0

for opt in "${@}"; do
    case "$opt" in
    -y | --yes)
        YES='on'
        ;;
    esac
done

for opt in "${@}"; do
    case "$opt" in
    -h | --help)
        display_usage
        exit 0
        ;;
    -s | --setup)
        MODE='SETUP'
        setup
        EXIT_CODE=$((EXIT_CODE + $?))
        ;;
    -t | --test)
        MODE='TEST'
        python3 -m unittest
        EXIT_CODE=$((EXIT_CODE + $?))
        ;;
    -c | --cleanup)
        MODE='CLEANUP'
        cleanup
        EXIT_CODE=$((EXIT_CODE + $?))
        ;;
    build | Build | BUILD)
        MODE='BUILD'
        BUILD='on'
        ;;
    install | Install | INSTALL)
        MODE='BUILD'
        INSTALL='on'
        ;;
    esac
done

# Defaul CLI call with no arguments
if [[ ${#@} -eq 0 ]]; then
    BUILD='on'
fi

if [[ "${MODE}" == 'BUILD' ]]; then
    init_build_wizzard
    EXIT_CODE=$?
fi

exit $EXIT_CODE

