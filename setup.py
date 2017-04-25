from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name='droplet',
    version='0.1.0',
    description='Python toolkit for creating and manipulating Diffusion Limited Aggregates.',
    long_description=long_descr,
    url='https://github.com/SJR276/droplet',
    author='Samuel Rowlinson',
    license='LGPL-3.0',
)
