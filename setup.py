import os
from setuptools import setup, find_packages
from codecs import open

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name='droplet',
    version='0.1.0',
    description='Python toolkit for creating and manipulating Diffusion Limited Aggregates.',
    long_description=long_descr,
    url='https://github.com/SJR276/droplet',
    author='Samuel Rowlinson',
    license='LGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='aggregates diffusion fractals physics visualization',
    packages=find_packages(exclude=['example_images', 'tests']),
    install_requires=['numpy', 'matplotlib', 'mpl_toolkits'],
)
