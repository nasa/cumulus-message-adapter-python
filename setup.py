# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import imp


here = path.abspath(path.dirname(__file__))

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' in x]

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

__version__ = imp.load_source('version', 'version.py').__version__

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='cumulus_message_adapter_python',  # Required

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version=__version__,  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='A handler library for cumulus tasks written in python',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/cumulus-nasa/cumulus-message-adapter-python',  # Optional
    author='Cumulus Authors',  # Optional
    author_email='info@developmentseed.org',  # Optional
    classifiers=[  # Optional
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='nasa cumulus',  # Optional
    packages=find_packages(exclude=['.circleci', 'contrib', 'docs', 'tests']),
    py_modules=['run_cumulus_task', 'cumulus_logger'],
    install_requires=install_requires,
    dependency_links=dependency_links
)
