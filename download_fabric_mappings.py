import argparse
import os.path
import shutil
from distutils import dir_util

import pygit2

from util import download_file, error

repo_path = os.path.join(os.path.dirname(__file__), "yarn")

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true", default=False, help="Delete mappings if they already exist")
parser.add_argument("--intermediary", action="store_true", default=False, help="Downloads intermediary mappings")
parser.add_argument("versions", metavar="version", nargs="+", help="Version to download mappings for")
args = parser.parse_args()


def setup_mappings_repo(version_tag):
    if not os.path.exists(repo_path):
        print("cloning yarn repository to {}".format(repo_path))
        pygit2.clone_repository("https://github.com/FabricMC/yarn.git", repo_path)

    repo = pygit2.Repository(repo_path)
    branch_name = f"origin/{version_tag}".replace(" ", "_")
    branch = repo.branches.get(branch_name)
    if branch is None:
        error("yarn repository has no remote {}".format(branch_name))

    repo.remotes[0].fetch()

    print("checking out {}".format(branch_name))
    ref = repo.lookup_reference(branch.name)
    commit = repo.get(branch.target)
    repo.checkout(ref)
    repo.reset(commit.id, pygit2.GIT_RESET_HARD)


def get_yarn_mappings(version, directory):
    mappings_dir = os.path.join(directory, "yarn_mappings")
    if os.path.exists(mappings_dir):
        if args.force:
            print("removing {}".format(mappings_dir))
            shutil.rmtree(mappings_dir)
        else:
            error("{} already exists and --force not specified, quitting".format(mappings_dir))

    os.mkdir(mappings_dir)
    setup_mappings_repo(version)
    dir_util.copy_tree(os.path.join(repo_path, "mappings"), mappings_dir)
    print("mappings saved to {}".format(mappings_dir))


def get_intermediary_mappings(version, directory):
    intermediary_path = os.path.join(directory, f"{version}.tiny")
    if not os.path.exists(intermediary_path):
        print("downloading {}".format(intermediary_path))
        download_file(f"https://github.com/FabricMC/intermediary/raw/master/mappings/{version}.tiny", intermediary_path)

    print("mappings saved to {}".format(intermediary_path))

def main():
    for version in args.versions:
        directory = os.path.join("versions", version)
        if not os.path.exists(directory):
            error("folder {} doesn't exist, have you run the downloader?".format(directory))

        if args.intermediary:
            get_intermediary_mappings(version, directory)
        else:
            get_yarn_mappings(version, directory)


main()
