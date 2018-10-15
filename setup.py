#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from os.path import abspath, dirname, join
from setuptools import setup


currdir = abspath(dirname(__file__))
with open(join(currdir, 'README.md')) as f:
    long_descr = f.read()

setup(
  name = "tinyscript",
  packages = ["tinyscript"],
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  version = "1.0.2",
  license = "AGPLv3",
  url = "https://github.com/dhondta/tinyscript",
  download_url = "https://github.com/dhondta/tinyscript/archive/1.0.2.tar.gz",
  description = "A library for quickly building CLI Python-based tools with "
                "basic features in a shortened way",
  long_description=long_descr,
  long_description_content_type='text/markdown',
  scripts = ["tinyscript-new"],
  keywords = ["CLI", "tool"],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Topic :: Security',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  python_requires = '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,<4',
)
