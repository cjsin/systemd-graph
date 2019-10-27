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

function err()
{
    msg "ERROR:" "${@}"
}

function run()
{
    msg "${@}"
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

    pp=""
    for arg in "${ADDPATHS[@]}"
    do
        arg=$(readlink -f "${arg}")
        pp="${pp}${pp:+:}${arg}"
    done

    PYTHONPATH="${pp}${PYTHONPATH:+:}${PYTHONPATH}"
    msg export PYTHONPATH="${PYTHONPATH}"
    export PYTHONPATH="${PYTHONPATH}"

    set -e
    case "${MODE}" in
        cd)
            msg cd "${SRCDIR}" "&&" run python3 -m pytest "${mod[@]}"
            cd "${SRCDIR}" && run python3 -m pytest "${mod[@]}"
            ;;
        path)
            msg "Running pytest-3 with PYTHONPATH setting and flags: ${same[*]}"
            run pytest "${same[@]}"
            ;;
        *)
            err "Unrecognised mode: ${mode}"
            ;;
    esac

}

msg "${0}" "${@}"
main "${@}"
