import os
import subprocess
import sys

from util import error, get_classpath

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

merged_path = os.path.join(version_dir, f"{version}-merged.jar")
if not os.path.exists(merged_path):
    error("missing merged jar")

tiny_path = os.path.join(version_dir, f"{version}.tiny")
if not os.path.exists(tiny_path):
    error("missing intermediates")

output_path = os.path.join(version_dir, f"{version}-intermediates.jar")
if os.path.exists(output_path):
    error("{} already exists, quitting".format(output_path))

classpath = get_classpath(version, version_dir)

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
