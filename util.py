import json
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


def get_classpath(version, version_dir):
    version_meta_path = os.path.join(version_dir, f"{version}.json")
    if not os.path.exists(version_meta_path):
        error("missing version meta")

    with open(version_meta_path, "rt") as file:
        version_meta = json.load(file)

    classpath = []
    libraries_path = os.path.join(version_dir, "libraries")
    if not os.path.exists(libraries_path):
        error("missing libraries")

    for library in version_meta["libraries"]:
        package, name, version, library_dir = extract_library_info(libraries_path, library)
        file_name = f"{name}-{version}.jar"
        library_path = os.path.join(library_dir, file_name)
        if not os.path.exists(library_dir) or not os.path.exists(library_path):
            error("failed to load library {} version {}".format(name, version))
            continue

        classpath.append(os.path.abspath(library_path))

    return classpath


def download_file(url, output_path):
    with c.request("GET", url, preload_content=False) as res, open(output_path, "wb") as out_file:
        copyfileobj(res, out_file)


def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)
