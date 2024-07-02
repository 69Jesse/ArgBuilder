from setuptools import (
    find_packages,
    setup,
)


setup(
    name='argbuilder',
    author='Jesse Janssen',
    url='https://github.com/69Jesse/ArgBuilder',
    version='0.3.2',
    packages=find_packages(),
    description='Arguments builder for creating console applications',
    python_requires='>=3.12',
    include_package_data=True,
)
