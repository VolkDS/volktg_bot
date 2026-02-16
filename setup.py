import os
import setuptools


def get_version():
    sc_version = os.environ.get("BUILD_VERSION")
    version = sc_version if sc_version else "0.0.0"
    return version


setuptools.setup(
    version=get_version(),
)
