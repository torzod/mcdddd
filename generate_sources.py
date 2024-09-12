import os
import subprocess
import sys
from util import download_file, error

if len(sys.argv) != 2:
    error("Usage: {} <version>".format(sys.argv[0]))

tool_dir = os.path.join(os.path.dirname(__file__), "tools")
os.makedirs(tool_dir, exist_ok=True)

cfr_path = os.path.join(tool_dir, "cfr-0.152.jar")
if not os.path.exists(cfr_path):
    print("downloading cfr-0.152.jar")
    download_file("https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar", cfr_path)

version = sys.argv[1]
version_dir = os.path.join("versions", version)
if not os.path.exists(version_dir):
    error("folder {} doesn't exist, have you run the downloader?".format(version_dir))

deobfuscated_path = os.path.join(version_dir, f"{version}-deobf.jar")
if not os.path.exists(deobfuscated_path):
    error("missing {}, have you run the deobfuscate_merged script?".format(deobfuscated_path))

sources_path = os.path.join(version_dir, "sources")
if os.path.exists(sources_path):
    error("{} already exists, quitting".format(sources_path))

process = subprocess.run([
    "java", "-Xmx2G", "-jar",
    os.path.abspath(cfr_path),
    os.path.abspath(deobfuscated_path),
    "--outputdir", os.path.abspath(sources_path),
    "--trackbytecodeloc", "true",
    "--hideutf", "false",
    "--comments", "false",
    "--showversion", "false"
], check=True)
print(f"version {version} sources saved to {sources_path}")