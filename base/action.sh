#!/system/bin/sh
MODPATH=${0%/*}
PATH=$PATH:/data/adb/ap/bin:/data/adb/magisk:/data/adb/ksu/bin

# log
exec 2> $MODPATH/logs/action.log
set -x

. $MODPATH/utils.sh

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
        return 0
    fi
}

[ -f $MODPATH/disable ] && {
    echo "[-] FakeHttp is disable"
    string="description=Run fakehttp on boot: ❌ (failed)"
    sed -i "s/^description=.*/$string/g" $MODPATH/module.prop
    sleep 1
    exit 0
}

load_config

set -- -d -z

[ -n "${interface+x}" ] && set -- "$@" "-i" "$interface"
[ -n "${hostname+x}" ] && set -- "$@" "-h" "$hostname"
[ -n "${mark+x}" ] && set -- "$@" "-m" "$mark"
[ -n "${mask+x}" ] && set -- "$@" "-x" "$mask"
[ -n "${number+x}" ] && set -- "$@" "-n" "$number"
[ -n "${repeat+x}" ] && set -- "$@" "-r" "$repeat"
[ -n "${payload+x}" ] && set -- "$@" "-b" "$payload"
[ -n "${logfile+x}" ] && set -- "$@" "-w" "$logfile"
[ -n "${ttl+x}" ] && set -- "$@" "-t" "$ttl"

result="$(busybox pgrep 'fakehttp')"
if [ $result -gt 0 ]; then
    echo "[-] Stopping fakehttp..."
    $MODPATH/bin/fakehttp -k
else
    echo "[-] Starting fakehttp..."
    $MODPATH/bin/fakehttp "$@"
fi

sleep 1

check_fakehttp_is_up 1

#EOF
