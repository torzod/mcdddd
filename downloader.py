import argparse
from json import load
from os import path, makedirs

from util import download_file, extract_library_info, process_server_jar


def download_libraries(directory, version_meta):
    for library in version_meta["libraries"]:
        package, name, version, library_dir = extract_library_info(directory, library)
        if not path.exists(library_dir):
            makedirs(library_dir)

        file_name = f"{name}-{version}.jar"
        library_path = path.join(library_dir, file_name)
        if path.exists(library_path):
            print("library {} version {} already downloaded, skipping".format(name, version))
            continue

        artifact = library["downloads"]["artifact"]
        print("downloading library {}".format(file_name))
        download_file(artifact["url"], library_path)


parser = argparse.ArgumentParser(description="Downloads Minecraft versions and their mappings, if applicable.")
parser.add_argument("--server", action="store_true", default=False, help="Downloads server versions")
parser.add_argument("--libraries", action="store_true", default=False, help="Downloads version libraries")
parser.add_argument("--force-version", action="append", default=[], metavar="version",
                    help="Downloads a version even if there are no mappings for it")
args = parser.parse_args()


def main():
    version_manifest_v2_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    experimental_versions_url = "https://maven.fabricmc.net/net/minecraft/experimental_versions.json"

    print("downloading version_manifest_v2.json from mojang")
    download_file(version_manifest_v2_url, "version_manifest_v2.json")

    print("downloading experimental_versions.json from fabric")
    download_file(experimental_versions_url, "experimental_versions.json")

    with open("version_manifest_v2.json", "rt") as file:
        manifest_v2 = load(file)

    with open("experimental_versions.json", "rt") as file:
        experimental_versions = load(file)

    if not path.exists("./versions/"):
        makedirs("./versions")

    has_forced_version = len(args.force_version) > 0
    all_versions = manifest_v2["versions"] + experimental_versions["versions"]

    for version in all_versions:
        version_id = version["id"]
        directory = f"./versions/{version_id}"
        filepath = f"{directory}/{version_id}.json"
        url = version["url"]

        if not path.exists(directory):
            makedirs(directory)

        if not path.isfile(filepath):
            print(f"downloading {version_id}.json")
            download_file(url, filepath)

        with open(filepath, "rt") as file:
            version_meta = load(file)
            has_mappings = "client_mappings" in version_meta["downloads"]

            if (has_forced_version and version_id in args.force_version) or (not has_forced_version and has_mappings):
                client = version_meta["downloads"]["client"]
                client_filename = f"{directory}/{version_id}-client"
                if not path.isfile(client_filename + ".jar"):
                    print(f"downloading {version_id}-client.jar")
                    download_file(client["url"], client_filename + ".jar")

                if args.server:
                    server = version_meta["downloads"]["server"]
                    server_filename = f"{directory}/{version_id}-server"
                    if not path.isfile(server_filename + ".jar"):
                        print(f"downloading {version_id}-server.jar")
                        download_file(server["url"], f"{server_filename}-intermediate.jar")
                    process_server_jar(directory, server_filename)

                if args.libraries:
                    libraries_path = path.join(directory, "libraries")
                    if not path.exists(libraries_path):
                        makedirs(libraries_path)
                    download_libraries(libraries_path, version_meta)

                if has_mappings and not path.isfile(client_filename + ".txt"):
                    client_mappings = version_meta["downloads"]["client_mappings"]
                    print(f"downloading {version_id}-client.txt")
                    download_file(client_mappings["url"], client_filename + ".txt")


main()
