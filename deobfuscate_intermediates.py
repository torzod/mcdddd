import json
import os
import subprocess
import sys

from util import error, extract_library_info

if len(sys.argv) != 2:
    error("Usage: {} <version>".format(sys.argv[0]))

tool_dir = os.path.join(os.path.dirname(__file__), "tools")
os.makedirs(tool_dir, exist_ok=True)

# ucky hack until my pr is merged
remapper_path = os.path.join(tool_dir, "tiny-remapper-0.10.4+local-fat.jar")
if not os.path.exists(remapper_path):
    # print("downloading tiny-remapper-0.9.0-fat.jar")
    # download_file("https://maven.fabricmc.net/net/fabricmc/tiny-remapper/0.9.0/tiny-remapper-0.9.0-fat.jar",
    #               remapper_path)
    error("tiny remapper not found: get from https://github.com/claiwe/tiny-remapper")

version = sys.argv[1]
version_dir = os.path.join("versions", version)
if not os.path.exists(version_dir):
    error("folder {} doesn't exist, have you run the downloader?".format(version_dir))

version_meta_path = os.path.join(version_dir, f"{version}.json")
if not os.path.exists(version_meta_path):
    error("missing version meta")

with open(version_meta_path, "rt") as file:
    version_meta = json.load(file)

merged_path = os.path.join(version_dir, f"{version}-merged.jar")
if not os.path.exists(merged_path):
    error("missing merged jar")

tiny_path = os.path.join(version_dir, f"{version}.tiny")
if not os.path.exists(tiny_path):
    error("missing intermediates")

output_path = os.path.join(version_dir, f"{version}-intermediates.jar")
if os.path.exists(output_path):
    error("{} already exists, quitting".format(output_path))

libraries_path = os.path.join(version_dir, "libraries")
if not os.path.exists(libraries_path):
    error("missing libraries")

classpath = []
for library in version_meta["libraries"]:
    package, name, version, library_dir = extract_library_info(libraries_path, library)
    file_name = f"{name}-{version}.jar"
    library_path = os.path.join(library_dir, file_name)
    if not os.path.exists(library_dir) or not os.path.exists(library_path):
        error("failed to load library {} version {}".format(name, version))
        continue

    classpath.append(os.path.abspath(library_path))

process_args = [
    "java", "-Xmx2G", "-jar",
    os.path.abspath(remapper_path),
    os.path.abspath(merged_path),
    os.path.abspath(output_path),
    os.path.abspath(tiny_path),
    "official", "intermediary"
]
process_args.extend(classpath)
process_args.extend([
    "--renameinvalidlocals",
    "--rebuildsourcefilenames",
    "--invalidlvnamepattern=\\$\\$\\d+",
    "--infernamefromsamelvindex"
])

process = subprocess.run(process_args, check=True, capture_output=True, text=True)
