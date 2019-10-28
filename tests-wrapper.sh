#!/bin/bash

# Shitty pytest has no command line option to even specify
# the top level of the source tree. The only options we have are to:
#   - put a __init__.py file in every directory
#   - cd into the toplevel dir and then run python3 -m pytest from there
#        ( including fixing all paths that were on the commandline)
#   - set PYTHONPATH before running pytest

function msg()
{
    echo "${@}" 1>&2
}

function verb()
{
    if (( ${VERBOSE:+0} ))
    then
        msg "${@}"
    fi
}

function err()
{
    msg "ERROR:" "${@}"
}

function run()
{
    verb "${@}"
    "${@}"
}

function usage()
{
    msg "Usage: ${0##*/} [-h|-help|--help|help] [--top=<dir>] [--src=<src>] <pytest-options>..."
    msg ""
    msg "Run pytest for a particular source folder"
}

function main()
{
    local MODE="path"
    local TOPDIR=""
    local SRCDIR=""
    local -a ADDPATHS=()

    local arg
    while (( $# ))
    do

        arg="${1}"
        case "${arg}" in
            -h|-help|--help|help)
                shift
                usage
                exit 0
                ;;
            --top=*)
                TOPDIR="${arg#*=}"
                shift
                ;;
            --src=*)
                SRCDIR="${arg#*=}"
                shift
                ;;
            --mode=*)
                MODE="${arg#*=}"
                shift
                ;;
            --path=*)
                ADDPATHS+=("${arg#*=}")
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    TOPDIR="${TOPDIR:-${PWD}}"
    TOPDIR="${TOPDIR%/}"

    if [[ -z "${SRCDIR}" ]]
    then
        SRCDIR="${TOPDIR}/src"
    elif [[ "${SRCDIR:0:1}" != "/" ]]
    then
        SRCDIR="${TOPDIR}/${SRCDIR}"
    fi

    SRCDIR="${SRCDIR%/}"

    SRCDIR=$(readlink -f "${SRCDIR}")
    nSRCDIR="${#SRCDIR}"

    local -a same=()
    local -a mod=()
    while (( $# ))
    do
        arg="${1}"
        shift
        same+=("${arg}")
        local modified="${arg}"
        local is_file_or_dir=0

        [[ -d "${arg}" ]] && is_file_or_dir=1
        [[ -f "${arg}" ]] && is_file_or_dir=1

        if (( is_file_or_dir ))
        then
            local check="${arg}"
            if [[ "${check:0:1}" != "/" ]]
            then
                check=$(readlink -f "${arg}")
            fi
            if [[ "${check:0:1}" == "/" ]]
            then
                if [[ "${check:0:${nSRCDIR}}" == "${SRCDIR}" ]]
                then
                    modified="${check:${nSRCDIR}}"
                fi
            fi
            mod+=("${modified}")
        fi
    done

    case "${MODE}" in
        path)
            ADDPATHS+=("${SRCDIR}")
            ;;
    esac

    local -A added=()
    local -a pp=()
    local -a new_pp=()
    IFS=: read -a pp <<< "${PYTHONPATH}"

    local arg
    for arg in "${ADDPATHS[@]}" "${pp[@]}"
    do
        if [[ -n "${arg}" ]]
        then
            arg=$(readlink -f "${arg}")
            if [[ -z "${added["${arg}"]}" ]]
            then
                added["${arg}"]=1
                new_pp+=("${arg}")
            fi
        fi
    done

    PYTHONPATH=""
    for arg in "${new_pp[@]}"
    do
        PYTHONPATH="${PYTHONPATH}${PYTHONPATH:+:}${arg}"
    done

    verb export PYTHONPATH="${PYTHONPATH}"
    export PYTHONPATH

    PYTEST="${PYTEST:-pytest-3}"
    PYTHON="${PYTHON:-python3}"

    set -e
    case "${MODE}" in
        cd)
            verb cd "${SRCDIR}" "&&" run ${PYTHON} -m pytest "${mod[@]}"
            cd "${SRCDIR}" && run ${PYTHON} -m pytest "${mod[@]}"
            ;;
        path)
            verb "Running ${PYTEST} with PYTHONPATH setting and flags: ${same[*]}"
            run ${PYTEST} "${same[@]}"
            ;;
        *)
            err "Unrecognised mode: ${mode}"
            ;;
    esac

}

verb "${0}" "${@}"
main "${@}"
