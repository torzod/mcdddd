import argparse
import os
import subprocess

from util import error, get_classpath

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--from-ns",  default="official", help="Namespace to remap from")
parser.add_argument("--to-ns", default="intermediary", help="Namespace to remap to")
parser.add_argument("--input", default="{}-merged.jar", help="Input jar path")
parser.add_argument("--tiny", default="{}.tiny", help="Input tiny mappings file")
parser.add_argument("--output", default="{}-intermediates.jar", help="Output jar path")
parser.add_argument("version", help="Which version to remap")
args = parser.parse_args()

tool_dir = os.path.join(os.path.dirname(__file__), "tools")
os.makedirs(tool_dir, exist_ok=True)

# ucky hack until my pr is merged
remapper_path = os.path.join(tool_dir, "tiny-remapper-0.10.4+local-fat.jar")
if not os.path.exists(remapper_path):
    # print("downloading tiny-remapper-0.9.0-fat.jar")
    # download_file("https://maven.fabricmc.net/net/fabricmc/tiny-remapper/0.9.0/tiny-remapper-0.9.0-fat.jar",
    #               remapper_path)
    error("tiny remapper not found: get from https://github.com/claiwe/tiny-remapper")

version = args.version
version_dir = os.path.join("versions", version)
if not os.path.exists(version_dir):
    error("folder {} doesn't exist, have you run the downloader?".format(version_dir))

input_path = os.path.join(version_dir, args.input.format(version))
if not os.path.exists(input_path):
    error("missing input file")

tiny_path = os.path.join(version_dir, args.tiny.format(version))
if not os.path.exists(tiny_path):
    error("missing tiny file")

output_path = os.path.join(version_dir, args.output.format(version))
if os.path.exists(output_path):
    error("{} already exists, quitting".format(output_path))

classpath = get_classpath(version, version_dir)

process_args = [
    "java", "-Xmx2G", "-jar",
    os.path.abspath(remapper_path),
    os.path.abspath(input_path),
    os.path.abspath(output_path),
    os.path.abspath(tiny_path),
    args.from_ns, args.to_ns
]
process_args.extend(classpath)
process_args.extend([
    "--renameinvalidlocals",
    "--rebuildsourcefilenames",
    "--invalidlvnamepattern=\\$\\$\\d+",
    "--infernamefromsamelvindex"
])

process = subprocess.run(process_args, check=True, capture_output=True, text=True)
