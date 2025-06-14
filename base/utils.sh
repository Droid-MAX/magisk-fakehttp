#!/bin/sh
MODPATH=${0%/*}
PATH=$PATH:/data/adb/ap/bin:/data/adb/magisk:/data/adb/ksu/bin

# log
exec 2> $MODPATH/logs/utils.log
set -x

function check_fakehttp_is_up() {
    [ ! -z "$1" ] && timeout="$1" || timeout=4
    counter=0

    while [ $counter -lt $timeout ]; do
        local result="$(busybox pgrep 'fakehttp')"
        if [ $result -gt 0 ]; then
            echo "[-] FakeHttp is running... 💉😜"
            string="description=Run fakehttp on boot: ✅ (active)"
            break
        else
            echo "[-] Checking fakehttp status: $counter"
            counter=$((counter + 1))
        fi
        sleep 1.5
    done

    if [ $counter -ge $timeout ]; then
        string="description=Run fakehttp on boot: ❌ (failed)"
    fi

    sed -i "s/^description=.*/$string/g" $MODPATH/module.prop
}

wait_for_boot() {
  while true; do
    local result="$(getprop sys.boot_completed)"
    if [ $? -ne 0 ]; then
      exit 1
    elif [ "$result" = "1" ]; then
      break
    fi
    sleep 3
  done

  # we doesn't have the permission to rw "/sdcard" before the user unlocks the screen
  local test_file="/sdcard/Android/.PERMISSION_TEST"
  true > "$test_file"
  while [ ! -f "$test_file" ]; do
    true > "$test_file"
    sleep 1
  done
  rm "$test_file"
}

#EOF
