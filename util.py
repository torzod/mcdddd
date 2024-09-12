from shutil import copyfileobj

from urllib3 import PoolManager

c = PoolManager()


def download_file(url, output_path):
    with c.request("GET", url, preload_content=False) as res, open(output_path, "wb") as out_file:
        copyfileobj(res, out_file)