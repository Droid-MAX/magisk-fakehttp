#!/bin/sh
# This script will be executed in late_start service mode
MODPATH=${0%/*}

# log
exec 2> $MODPATH/logs/service.log
set -x

. $MODPATH/utils.sh || exit $?

wait_for_boot

# Load config
load_config() {
    # Check for config first
    local internal_config="/sdcard/.fakehttp.conf"
    local module_config="$MODPATH/conf/fakehttp.conf"
    if [ -f "$internal_config" ]; then
        source "$internal_config"
        return 0
    elif [ -f "$module_config" ] && [ ! -f "$internal_config" ]; then
        cp "$module_config" "$internal_config" && source "$internal_config"
        return 0
    else
        interface="wlan0"
        hostname="www.speedtest.cn"
        logfile="/sdcard/.fakehttp.log"
        silent="1"
        return 0
    fi
}

load_config

set -- -d -z

[ -n "${interface+x}" ] && { [ "$interface" == "all" ] && set -- "$@" "-a" || set -- "$@" "-i" "$interface"; }
[ -n "${hostname+x}" ] && set -- "$@" "-h" "$hostname" "-e" "$hostname"
[ -n "${mark+x}" ] && set -- "$@" "-m" "$mark"
[ -n "${mask+x}" ] && set -- "$@" "-x" "$mask"
[ -n "${number+x}" ] && set -- "$@" "-n" "$number"
[ -n "${repeat+x}" ] && set -- "$@" "-r" "$repeat"
[ -n "${payload+x}" ] && set -- "$@" "-b" "$payload"
[ -n "${logfile+x}" ] && set -- "$@" "-w" "$logfile"
[ -n "${silent+x}" ] && [ "$silent" -eq 1 ] && set -- "$@" "-s"
[ -n "${ttl+x}" ] && set -- "$@" "-t" "$ttl"
[ -n "${pct+x}" ] && set -- "$@" "-y" "$pct"

$MODPATH/bin/fakehttp "$@"

check_fakehttp_is_up

#EOF
