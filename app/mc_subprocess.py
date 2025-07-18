from nicegui import ui
import asyncio
import os
import re
import subprocess
from subprocess import CalledProcessError
from urllib.parse import urlparse

_sp_common = {"capture_output": True, "text": True, "check": True}
_column_sep = "###"


def _create_table_header(headers):
    return [{"name": h, "label": h, "field": h, "align": "left"} for h in headers]


def _parse_table(stdout):
    lines = stdout.strip().splitlines()
    if len(lines) < 2:
        return [], []
    headers = lines[0].split(_column_sep)
    columns = _create_table_header(headers)
    rows = []
    for line in lines[1:]:
        if not line.strip():
            break
        row = dict(zip(headers, line.split(_column_sep)))
        rows.append(row)
    return columns, rows


def _parse_table_fixed(stdout):
    lines = stdout.rstrip().splitlines()
    if len(lines) < 2:
        return [], []

    headers = []
    header = lines[0]
    col_starts = []

    for match in re.finditer(r"\S+", header):
        col_starts.append(match.start())
        headers.append(match.group())

    col_starts.append(len(header) + 1)
    columns = _create_table_header(headers)

    rows = []
    for line in lines[1:]:
        if not line.strip():
            break
        fields = [
            line[col_starts[i] : col_starts[i + 1]].strip() for i in range(len(headers))
        ]
        row = dict(zip(headers, fields))
        rows.append(row)
    return columns, rows


def notify_wrapper(func):
    def wrapped(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            ui.notify("Done", color="positive")
            return result
        except CalledProcessError as e:
            ui.notify(f"Error: {e.stderr}", color="negative")
            return None

    return wrapped


def version():
    try:
        result = subprocess.run(["mega-version"], **_sp_common)
        version = ""
        raw = result.stdout.strip()
        match = re.search(r"(?<=MEGAcmd version:\s)(\d+\.\d+\.\d+\.\d+)", raw)
        if match:
            version = "MEGAcmd " + match.group(0)
        return version
    except CalledProcessError:
        return ""


def whoami():
    try:
        result = subprocess.run(["mega-whoami"], **_sp_common)
        whoami = ""
        raw = result.stdout.strip()
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw)
        if match:
            whoami = match.group(0)
        return whoami
    except CalledProcessError:
        return ""


def is_logged_in():
    return whoami() != ""


async def login(email, password):
    try:
        proc = subprocess.Popen(
            ["mega-login", email, password],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        while proc.poll() is None:
            await asyncio.sleep(0.5)
    except CalledProcessError:
        return ""


@notify_wrapper
def logout():
    return subprocess.run(["mega-logout"], **_sp_common)


def ls(path, is_remote=False):
    try:
        if not is_remote:
            result = subprocess.run(
                f'ls -1F "{path}" | grep "/$"',
                shell=True,
                **_sp_common,
            )
            dirs = []
            lines = result.stdout.strip().splitlines()
            for line in lines:
                dir = line.removesuffix("/")
                if dir.strip() != "":
                    dirs.append(dir)
        else:
            result = subprocess.run(
                f'mega-ls -a "{path}" | grep "(folder)$"',
                shell=True,
                **_sp_common,
            )
            dirs = []
            lines = result.stdout.strip().splitlines()
            for line in lines:
                dir = line.removesuffix(" (folder)")
                if dir.strip() != "":
                    dirs.append(dir)

        return sorted(dirs)
    except CalledProcessError:
        return []


@notify_wrapper
def mkdir(path, new_dir, is_remote=False):
    full_path = os.path.join(path, new_dir)
    cmd = "mkdir"
    if is_remote:
        cmd = "mega-mkdir"
    return subprocess.run([cmd, full_path], **_sp_common)


def list_syncs():
    try:
        result = subprocess.run(
            ["mega-sync", f"--col-separator={_column_sep}"],
            **_sp_common,
        )
        columns, rows = _parse_table(stdout=result.stdout)
        return columns, rows
    except CalledProcessError:
        return [], []


@notify_wrapper
def add_sync(local_path, remote_path):
    return subprocess.run(
        ["mega-sync", local_path, remote_path],
        **_sp_common,
    )


@notify_wrapper
def remove_sync(local_path):
    return subprocess.run(["mega-sync", "-d", local_path], **_sp_common)


def list_sync_issues():
    try:
        result = subprocess.run(
            ["mega-sync-issues", f"--col-separator={_column_sep}"],
            **_sp_common,
        )
        columns, rows = _parse_table(stdout=result.stdout)
        return columns, rows
    except CalledProcessError:
        return [], []


def list_sync_issue_details(issue_id):
    try:
        result = subprocess.run(
            [
                "mega-sync-issues",
                f"--col-separator={_column_sep}",
                "--detail",
                issue_id,
            ],
            **_sp_common,
        )

        # Determine issue to deal with
        description, raw_table = result.stdout.split("\n\n", 1)
        columns, rows = _parse_table(stdout=raw_table)
        return description, columns, rows
    except CalledProcessError:
        return [], []


@notify_wrapper
def remove_sync_issue(path):
    if path.startswith("<CLOUD>"):
        remote_path = path[len("<CLOUD>") :]
        return subprocess.run(["mega-rm", "-r", "-f", remote_path], **_sp_common)
    else:
        return subprocess.run(["rm", "-rf", path], **_sp_common)


def list_webdavs(base_url=""):
    try:
        result = subprocess.run(["mega-webdav"], **_sp_common)
        headers = ["PATH", "URL"]
        columns = _create_table_header(headers)

        rows = []
        split_string = "http://"
        for line in result.stdout.strip().splitlines():
            if split_string in line:
                path, url = line.split(split_string, 1)
                path = path.strip(" :")
                url = split_string + url.strip()
                if base_url:
                    url_path = urlparse(url).path
                    url = base_url.rstrip("/") + url_path
                rows.append({"PATH": path, "URL": url})
        rows.sort(key=lambda e: e["PATH"])
        return columns, rows

    except CalledProcessError:
        return [], []


@notify_wrapper
def add_webdav(remote_path, is_public=False):
    cmd = ["mega-webdav", remote_path]
    if is_public:
        cmd.append("--public")
    return subprocess.run(cmd, **_sp_common)


@notify_wrapper
def remove_webdav(remote_path):
    return subprocess.run(
        ["mega-webdav", "-d", remote_path],
        **_sp_common,
    )


def list_backups():
    try:
        result = subprocess.run(["mega-backup"], **_sp_common)
        columns, rows = _parse_table_fixed(result.stdout)
        return columns, rows

    except CalledProcessError:
        return [], []


@notify_wrapper
def add_backup(local, remote, period, num):
    cmd = [
        "mega-backup",
        local,
        remote,
        f"--period={period}",
        f"--num-backups={num}",
    ]
    return subprocess.run(cmd, **_sp_common)


@notify_wrapper
def remove_backup(local):
    cmd = ["mega-backup", "-d", local]
    return subprocess.run(cmd, **_sp_common)


def list_mounts():
    try:
        result = subprocess.run(["mega-fuse-show"], **_sp_common)
        columns, rows = _parse_table_fixed(result.stdout)
        return columns, rows

    except CalledProcessError:
        return [], []


@notify_wrapper
def add_mount(
    local,
    remote,
    name=None,
    disabled=False,
    transient=False,
    read_only=False,
):
    cmd = ["mega-fuse-add"]
    if name:
        cmd.append(f"--name={name}")
    if disabled:
        cmd.append("--disabled")
    if transient:
        cmd.append("--transient")
    if read_only:
        cmd.append("--read-only")

    cmd += [local, remote]
    return subprocess.run(cmd, **_sp_common)


@notify_wrapper
def remove_mount(local_or_name):
    # Function still in experimental stage, umount must be forced
    # with fusermount before removing with megacmd (disabling does not work properly)
    cmd = f"fusermount -uz {local_or_name} && mega-fuse-remove {local_or_name}"
    return subprocess.run(cmd, shell=True, **_sp_common)
