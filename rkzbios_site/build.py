import subprocess
import os

NAME = "rkzbios-admin"


def build():
    tag = subprocess.check_output(["git", "describe"])[:-1].decode('utf-8')

    build_image = input("Build a image with version %s y/n ...  " % tag)

    if build_image == "y":


        name = "%s:%s" % (NAME, tag)
        registry_name = "dockerregistry.jimboplatform.nl/" + name

        cmd = ["sudo", "docker", "build","--no-cache", "-t", name, "."]
        #cmd = ["sudo", "docker", "build", "-t", name, "."]

        subprocess.call(cmd)

        cmd = ["sudo", "docker", "tag", name, registry_name]
        subprocess.call(cmd)

        to_docker_registry = input("Push docker image in  dockerregistry.jimboplatform.nl?   y/n ")
        if to_docker_registry == 'y':
            cmd = ["sudo", "docker", "login", "dockerregistry.jimboplatform.nl"]
            subprocess.call(cmd)

            cmd = ["sudo", "docker", "push", registry_name]
            subprocess.call(cmd)


build()