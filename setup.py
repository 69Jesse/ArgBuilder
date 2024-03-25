from setuptools import (
    find_packages,
    setup,
)


setup(
    name='scriptbuilder',
    author='Jesse Janssen',
    url='https://github.com/69Jesse/Aliases/tree/main/scripts/builder',
    version='0.2',
    packages=find_packages(),
    description='Arguments builder for creating console scripts',
    python_requires='>=3.12',
    include_package_data=True,
)
