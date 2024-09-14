import os
import subprocess
import sys

from util import download_file, error

if len(sys.argv) != 2 and len(sys.argv) != 3:
    error("Usage: {} <version>".format(sys.argv[0]))

use_intermediary = True if len(sys.argv) == 3 and sys.argv[2] == "--intermediary" else False
tool_dir = os.path.join(os.path.dirname(__file__), "tools")
os.makedirs(tool_dir, exist_ok=True)

enigma_path = os.path.join(tool_dir, "enigma-cli-2.5.1-all.jar")
if not os.path.exists(enigma_path):
    print("downloading enigma-cli-2.5.1-all.jar")
    download_file("https://maven.fabricmc.net/cuchaz/enigma-cli/2.5.1/enigma-cli-2.5.1-all.jar", enigma_path)

version = sys.argv[1]
version_dir = os.path.join("versions", version)
if not os.path.exists(version_dir):
    error("folder {} doesn't exist, have you run the downloader?".format(version_dir))

mappings_path = os.path.join(version_dir, "yarn_mappings")
if not os.path.exists(mappings_path):
    error("missing mappings")

merged_path = os.path.join(version_dir, f"{version}-intermediates.jar" if use_intermediary else f"{version}-merged.jar")
if not os.path.exists(merged_path):
    error("missing merged jar".format(merged_path))

deobfuscated_path = os.path.join(version_dir, f"{version}-deobf.jar")
if os.path.exists(deobfuscated_path):
    error("{} already exists, quitting".format(deobfuscated_path))

process = subprocess.run([
    "java", "-Xmx2G", "-cp",
    os.path.abspath(enigma_path),
    "cuchaz.enigma.command.Main",
    "deobfuscate",
    os.path.abspath(merged_path),
    os.path.abspath(deobfuscated_path),
    os.path.abspath(mappings_path)
], check=True, capture_output=True, text=True)