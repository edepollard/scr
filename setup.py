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
import os

# Read the README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='scr',
    version='1.0.0',
    description='A screen helper script to manage GNU screen sessions',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Ed Pollard',
    author_email='',
    url='',
    license='MIT',
    
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
    
    # Entry points - creates the 'scr' command
    entry_points={
        'console_scripts': [
            'scr=scr.scr:main',
        ],
    },
    
    # Scripts - alternative way to install the bin/scr script
    scripts=['bin/scr'],
    
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
            'vendor': 'Ed Pollard',
        }
    },
)

