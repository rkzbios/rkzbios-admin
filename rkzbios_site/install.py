import os, sys, traceback, subprocess


def to_package_url(package, username, password):
    name, version = package.strip().split('==')
    return  "http://%(username)s:%(password)s@nexus.knowlogy.nl/repository/pypi/%(name)s/%(version)s/%(name)s-%(version)s-py3.tar.gz" % \
        {"username": username, "password": password, "version": version, "name": name}

def install_package(package, username, password):
    package_url = to_package_url(package, username, password)
    cmd = ["pip", "install", package_url]
    subprocess.call(cmd)

def pip_install_requirements(requirements_file, target = None):
    cmd = ["pip", "install", "-r", requirements_file]
    if target:
        cmd.append("--target=%s" % target)
    subprocess.call(cmd)


def install_packages(packages, nexus_username, nexus_password):
    for package in packages:
        install_package(package, nexus_username, nexus_password)


def get_package_lines(requirements_file_name):
    """
    Returns all requirements lines from a package, skips lines starting with #
    """
    package_lines = []
    with open(requirements_file_name) as requirements_file:
        requirement_lines = requirements_file.readlines()
        for requirement_line in requirement_lines:
            if not requirement_line.startswith("#"):
                package_lines.append(requirement_line)
    return package_lines

def install_requirements_nexus(requirements_filename, nexus_username, nexus_password):
    package_lines = get_package_lines(requirements_filename)
    install_packages(package_lines, nexus_username, nexus_password)


if __name__ == "__main__":
    import sys

    username = (sys.argv[1])
    password = (sys.argv[2])
    # pip_install_requirements("requirements.txt")
    install_requirements_nexus("requirements-nexus.txt", username,password)

