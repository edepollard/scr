#!/usr/bin/env python3
"""
Setup script for scr - Screen Session Manager

This setup.py allows for:
- Standard Python package installation (pip install .)
- Building RPM packages (python setup.py bdist_rpm)
- Building source distributions (python setup.py sdist)

This file created with AI Coding Assistant
"""

from setuptools import setup, find_packages
from configparser import ConfigParser
import os

# Read the README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

cfile = os.path.join(os.path.dirname(__file__), 'pkg_config.ini')
cp = ConfigParser()
if os.path.exists(cfile):
   with open(cfile, mode='r', encoding='utf-8') as pkg_config:
       cp.read_file(pkg_config)
else:
   raise FileNotFoundError("File 'pkg_config.ini' missing.")

pkg=cp.get('package','name',fallback='None')
version=cp.get('package','version',fallback='0.0.0')
desc=cp.get('package','description',fallback='None')
author=cp.get('package','author',fallback='None')
email=cp.get('package','author_email',fallback='None')
url=cp.get('package','url',fallback='None')
pkg_license=cp.get('package','liccense',fallback='MIT')

setup(
    name=pkg,
    version=version,
    description=desc,
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author=author,
    author_email=email,
    url=url,
    license=pkg_license,

    # Package configuration
    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    # Include non-Python files
    include_package_data=True,

    # Dependencies
    install_requires=[
        'click>=7.0',
    ],

    # Python version requirement
    python_requires='>=3.6',

    # Scripts - installs the bin/scr script as executable
    scripts=[f"bin/{pkg}"],

    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    # Keywords for searching
    keywords='screen gnu-screen session-manager terminal multiplexer',

    # RPM-specific options
    options={
        'bdist_rpm': {
            'requires': 'screen python3-click',
            'group': 'Development/Tools',
            'vendor': author,
        }
    },
)

