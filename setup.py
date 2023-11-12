#!/usr/bin/env python

# TODO - Make consumable artifact

import sys
import os
import pkgutil
import json

from setuptools import setup, find_packages
from kaya_module_sdk.sdk import Config

def find_file_recursively(directory, target_filename):
    for root, _, files in os.walk(directory):
        if target_filename in files:
            return os.path.join(root, target_filename)
    return None

# [ NOTE ]: Directory where this file is located
#   root_dir = os.path.abspath(os.path.dirname(__file__))
#   DEFAULT = {'conf-file': find_file_recursively('.', 'module.conf.json')}
#   conf = Config(DEFAULT['conf-file'])
#   METADATA = conf.METADATA

#   # MISCELLANEOUS

#   def add_package_dir_to_path() -> None:
#       '''
#       [ NOTE ]: Add the package directory to the Python path
#       '''
#       package_dir = os.path.join(root_dir, METADATA['MODULE_NAME'].lower())
#       sys.path.insert(0, package_dir)
#       for loader, name, is_pkg in pkgutil.walk_packages([package_dir]):
#           full_name = METADATA['MODULE_NAME'].lower() + '.' + name
#           if is_pkg:
#               path = loader.path
#           else:
#               path = os.path.dirname(loader.path)
#           sys.path.insert(0, path)

#   if __name__ == '__main__':
#       with open('README.md', 'r', encoding='utf-8') as fl:
#           readme_content = fl.read()
#       setup_info = {
#           'name': METADATA['MODULE_NAME'].lower(),
#           'version': METADATA['MODULE_VERSION'].lower(),
#           'author': '',
#           'author_email': '',
#           'url': 'https://kaya.wanolabs.com',
#           'download_url': METADATA['MODULE_URLS']['download'],
#           'project_urls': {
#               'Documentation': METADATA['MODULE_URLS']['documentation'],
#               'Source': METADATA['MODULE_URLS']['source'],
#               'Tracker': METADATA['MODULE_URLS']['tracker'],
#           },
#           'description': METADATA['MODULE_DESCRIPTION'],
#           'long_description': readme_content,
#           'long_description_content_type': 'text/markdown',
#           'license': 'BSD',
#           'classifiers': [
#               'Development Status :: 1 - Development/Unstable',
#               'Environment :: Linux',
#               'Environment :: AWS Cloud Applications',
#               'Intended Audience :: End Users',
#               'License :: ',
#               'Operating System :: POSIX :: Linux',
#               'Programming Language :: Python :: 3',
#               'Programming Language :: Python :: 3.8',
#               'Programming Language :: Python :: 3.9',
#               'Programming Language :: Python :: 3.10',
#               'Programming Language :: Python :: 3.11',
#               'Topic :: Financial/AlgoTrading',
#               'Topic :: Software Development :: Libraries :: Python Modules',
#           ],

#           # Package info
#           'packages': find_packages(),
#           'package_data': {
#               METADATA['MODULE_NAME'].lower(): [DEFAULT['conf-file']]
#           },

#           # Add _ prefix to the names of temporary build dirs
#           'options': {'build': {'build_base': '_build'}},
#           'zip_safe': True,

#           'test_suite': 'MAT',
#           'install_requires': ['flake8', 'mypy', 'pylint'],
#           'setup_requires': ['flake8'],
#           'entry_points': {},
#       }
#       add_package_dir_to_path()
#       setup(**setup_info)

