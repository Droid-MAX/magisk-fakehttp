#!/user/bin/env python3
import logging
import tarfile
import os
from pathlib import Path
import shutil
import threading
import zipfile
import concurrent.futures
import json
import re

import requests

PATH_BASE = Path(__file__).parent.resolve()
PATH_BASE_MODULE: Path = PATH_BASE.joinpath("base")
PATH_BUILD: Path = PATH_BASE.joinpath("build")
PATH_BUILD_TMP: Path = PATH_BUILD.joinpath("tmp")
PATH_DOWNLOADS: Path = PATH_BASE.joinpath("downloads")

logger = logging.getLogger()
syslog = logging.StreamHandler()
formatter = logging.Formatter("%(threadName)s : %(message)s")
syslog.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(syslog)


def download_file(url: str, path: Path):
    file_name = url[url.rfind("/") + 1 :]
    logger.info(f"Downloading '{file_name}' to '{path}'")

    if path.exists():
        return

    r = requests.get(url, allow_redirects=True)
    with open(path, "wb") as f:
        f.write(r.content)

    logger.info("Done")


def extract_file(archive_path: Path, dest_path: Path):
    logger.info(f"Extracting '{archive_path.name}' to '{dest_path.name}'")

    with tarfile.open(archive_path) as tar:
        for member in tar.getmembers():
            if member.name.endswith("fakehttp") and member.isfile():
                with tar.extractfile(member) as f:
                    file_content = f.read()

        path = dest_path.parent
        path.mkdir(parents=True, exist_ok=True)

        with open(dest_path, "wb") as out:
            out.write(file_content)


def generate_version_code(project_tag: str) -> int:
    parts = re.split("[-.]", project_tag)
    version_code = "".join(f"{int(part):02d}" for part in parts)
    return int(version_code)


def create_module_prop(path: Path, project_tag: str):
    module_prop = f"""id=magisk-fakehttp
name=MagiskFakehttp
version={project_tag}
versionCode={generate_version_code(project_tag)}
author=Mike Wang & Droid-MAX
updateJson=https://github.com/Droid-MAX/magisk-fakehttp/releases/latest/download/updater.json
description=Run fakehttp on boot"""

    with open(path.joinpath("module.prop"), "w", newline="\n") as f:
        f.write(module_prop)


def create_module_conf(path: Path):
    module_conf = '''#!/system/bin/sh

# network interface name (required)
interface="wlan0"
# hostname for obfuscation (required)
hostname="www.speedtest.cn"
# fwmark for bypassing the queue
#mark=""
# set the mask for fwmark
#mask=""
# netfilter queue number
#number=""
# duplicate generated packets for <repeat> times
#repeat=""
# use TCP payload from binary file (ignore hostname)
#payload=""
# write log to <file> instead of stderr
logfile="/sdcard/.fakehttp.log"
# silent mode
silent="1"
# TTL for generated packets (default: auto)
#ttl=""'''

    with open(path.joinpath("fakehttp.conf"), "w", newline="\n") as f:
        f.write(module_conf)


def create_module(project_tag: str):
    logger.info("Creating module")

    if PATH_BUILD_TMP.exists():
        shutil.rmtree(PATH_BUILD_TMP)

    shutil.copytree(PATH_BASE_MODULE, PATH_BUILD_TMP)
    create_module_prop(PATH_BUILD_TMP, project_tag)


def fill_module(arch: str, fakehttp_tag: str, project_tag: str):
    threading.current_thread().setName(arch)
    logger.info(f"Filling module for arch '{arch}'")

    fakehttp_download_url = (
        f"https://github.com/MikeWang000000/FakeHTTP/releases/download/{fakehttp_tag}/"
    )
    fakehttp_pkg = f"fakehttp-linux-{arch}.tar.gz"
    fakehttp_pkg_path = PATH_DOWNLOADS.joinpath(fakehttp_pkg)

    download_file(fakehttp_download_url + fakehttp_pkg, fakehttp_pkg_path)
    files_dir = PATH_BUILD_TMP.joinpath("files")
    files_dir.mkdir(exist_ok=True)
    extract_file(fakehttp_pkg_path, files_dir.joinpath(f"fakehttp-{arch}"))
    create_module_conf(files_dir)


def create_updater_json(project_tag: str):
    logger.info("Creating updater.json")

    updater = {
        "version": project_tag,
        "versionCode": generate_version_code(project_tag),
        "zipUrl": f"https://github.com/Droid-MAX/magisk-fakehttp/releases/download/{project_tag}/MagiskFakehttp-{project_tag}.zip",
        "changelog": "https://raw.githubusercontent.com/Droid-MAX/magisk-fakehttp/master/CHANGELOG.md",
    }

    with open(PATH_BUILD.joinpath("updater.json"), "w", newline="\n") as f:
        f.write(json.dumps(updater, indent=4))


def package_module(project_tag: str):
    logger.info("Packaging module")

    module_zip = PATH_BUILD.joinpath(f"MagiskFakehttp-{project_tag}.zip")

    with zipfile.ZipFile(module_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PATH_BUILD_TMP):
            for file_name in files:
                if file_name == "placeholder" or file_name == ".gitkeep":
                    continue
                zf.write(
                    Path(root).joinpath(file_name),
                    arcname=Path(root).relative_to(PATH_BUILD_TMP).joinpath(file_name),
                )

    shutil.rmtree(PATH_BUILD_TMP)


def do_build(fakehttp_tag: str, project_tag: str):
    PATH_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    PATH_BUILD.mkdir(parents=True, exist_ok=True)

    create_module(project_tag)

    archs = ["arm32v7", "arm64", "i686", "x86_64"]
    executor = concurrent.futures.ProcessPoolExecutor()
    futures = [
        executor.submit(fill_module, arch, fakehttp_tag, project_tag) for arch in archs
    ]
    for future in concurrent.futures.as_completed(futures):
        if future.exception() is not None:
            raise future.exception()

    package_module(project_tag)
    create_updater_json(project_tag)

    logger.info("Done")
