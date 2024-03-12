#!/bin/python3
import os
import xmltodict
import git
import argparse
import shutil
from urllib.parse import urlparse
from urllib.request import urlopen
from typing import Dict, Any

def get_manifest_url(repo_url: str, repo_tag: str, manifest_file: str) -> str:
    p = urlparse(repo_url)
    if "github" in p.netloc:
        return str.join('/', ["https://raw.githubusercontent.com",p.path, repo_tag, manifest_file])

def download_manifest(repo_url: str, repo_tag: str, manifest_file: str) -> Dict[str, Any]:
    """
    Download the repo manifest from the Git repository and parse remotes.

    Args:
        repo_url (str): The URL of the Git repository.
        manifest_file (str): The name of the manifest file.

    Returns:
        tuple: Parsed manifest data and dictionary of remotes.
    """
    manifest_path = get_manifest_url(repo_url, repo_tag, manifest_file)
    
    with urlopen(url = manifest_path) as f:
        manifest_data = xmltodict.parse(f.read())
    manifest_data['manifest']['remotes'] = {}
    if not isinstance(manifest_data['manifest']['project'], list):
        manifest_data['manifest']['project'] = [manifest_data['manifest']['project']]
    if 'manifest' in manifest_data:
        remote = manifest_data['manifest']['remote']
        manifest_data['manifest']['remotes'][remote['@name']] = remote['@fetch']

        if 'include' in manifest_data['manifest'] and '@name' in manifest_data['manifest']['include']:
            include = manifest_data['manifest']['include']
            if isinstance(include, list):
                for i in include:
                    manifest_data_included = download_manifest(repo_url, repo_tag, i['@name'])
                    manifest_data['manifest']['remotes'] |= manifest_data_included['manifest']['remotes']
                    manifest_data['manifest']['project'] += manifest_data_included['manifest']['project']
            else:
                manifest_data_included = download_manifest(repo_url, repo_tag, include['@name'])
                manifest_data['manifest']['remotes'] |= manifest_data_included['manifest']['remotes']
                manifest_data['manifest']['project'] += manifest_data_included['manifest']['project']
    return manifest_data

def add_submodules(manifest_data: Dict[str, Any]) -> None:
    """
    Add or update project tags as git submodules.

    Args:
        manifest_data (dict): Parsed manifest data.
        remotes (dict): Mapping of remote names to URLs.
    """
    repo = git.Repo()

    if 'manifest' in manifest_data and 'project' in manifest_data['manifest']:
        projects = manifest_data['manifest']['project']
        remotes = manifest_data['manifest']['remotes']
        for project in projects:
            url = remotes[project.get('@remote')]
            if url is None:
                raise ValueError(f"No URL found for remote '{project.get('@remote')}'")
            name = project['@name']
            tag = project['@revision']
            path= project['@path']
            
            submodule_path = os.path.join(repo.working_dir, path)
            if len(repo.submodules) > 0:
                if name in repo.submodules:
                    submodule = repo.submodule(name)
                    if submodule.branch_name != tag:
                        print(f"Updating submodule '{name}' from '{submodule.branch_name}' to '{tag}'")
                        submodule.update(recursive=True, init=True, force=True)
                        submodule.repo.git.checkout(tag)
            else:
                print(f"Adding submodule '{name}' using '{tag}'")
                repo.create_submodule(name=name, path=path, url = str.join('/',[ url, name ]), branch=tag)

            if 'copyfile' in project:
                shutil.copyfile(os.path.join(submodule_path, project['copyfile']["@src"]), os.path.join(repo.working_dir, project['copyfile']["@dest"]))

def initialize_git_directory() -> None:
    """
    Initialize the current directory as a git repository if it isn't already.
    """
    if not os.path.exists('.git'):
        git.Repo.init()

def main(repo_url: str, repo_tag: str = "main", manifest_file: str = "default.xml") -> None:
    """
    Main function to download repo manifest and add project tags as git submodules.

    Args:
        repo_url (str): The URL of the Git repository.
        manifest_file (str, optional): The name of the manifest file. Defaults to "default.xml".
    """
    initialize_git_directory()
    manifest_data = download_manifest(repo_url, repo_tag, manifest_file)
    add_submodules(manifest_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download repo manifest and add project tags as git submodules")
    parser.add_argument("-u", "--url", required=True, type=str, help="Git repository URL")
    parser.add_argument("-f", "--file", type=str, help="Manifest file name (default: default.xml)", default="default.xml")
    parser.add_argument("-b", "--branch", type=str, help="Branch or tag of the git repo", default="main")
    args = parser.parse_args()
    
    main(args.url, args.branch, args.file)