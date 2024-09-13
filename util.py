import os
import sys
from shutil import copyfileobj

from urllib3 import PoolManager

c = PoolManager()


def extract_library_info(directory, library):
    name_parts = library["name"].split(":")
    has_extra = len(name_parts) == 4
    if len(name_parts) != 3 and not has_extra:
        error("unable to parse library {}".format(library["name"]))

    package = name_parts[0]
    name = name_parts[1]
    version = name_parts[2]
    if has_extra:
        version += f"-{name_parts[3]}"

    library_dir = os.path.join(directory, os.sep.join(package.split(".")), name, version)
    return package, name, version, library_dir


def download_file(url, output_path):
    with c.request("GET", url, preload_content=False) as res, open(output_path, "wb") as out_file:
        copyfileobj(res, out_file)


def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)
