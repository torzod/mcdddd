import os
import json
import urllib3, shutil

c = urllib3.PoolManager()

with c.request("GET", "http://piston-meta.mojang.com/mc/game/version_manifest_v2.json", preload_content=False) as res, open("manifest-v2.json", "wb") as out_file:
    print("downloading manifest-v2.json")
    shutil.copyfileobj(res, out_file)

with open("manifest-v2.json", "rt") as file:
    manifest_v2 = json.load(file)

if not os.path.exists("./versions/"):
    os.makedirs("./versions")

for version in manifest_v2["versions"]:
    version_id = version["id"]
    directory = f"./versions/{version_id}"
    filepath = f"{directory}/{version_id}.json"
    url = version["url"]

    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.isfile(filepath):
        with c.request("GET", url, preload_content=False) as res, open(filepath, "wb") as out_file:
            print(f"downloading {version_id}.json")
            shutil.copyfileobj(res, out_file)

    with open(filepath, "rt") as file:
        version_meta = json.load(file)

        if "client_mappings" in version_meta["downloads"]:
            client = version_meta["downloads"]["client"]
            client_mappings = version_meta["downloads"]["client_mappings"]
            client_filename = f"{directory}/{version_id}-client"

            if not os.path.isfile(client_filename + ".jar"):
                with c.request("GET", client["url"], preload_content=False) as res, open(client_filename + ".jar", "wb") as out_file:
                    print(f"downloading {version_id}-client.jar")
                    shutil.copyfileobj(res, out_file)

            if not os.path.isfile(client_filename + ".txt"):
                with c.request("GET", client_mappings["url"], preload_content=False) as res, open(client_filename + ".txt", "wb") as out_file:
                    print(f"downloading {version_id}-client.txt")
                    shutil.copyfileobj(res, out_file)
