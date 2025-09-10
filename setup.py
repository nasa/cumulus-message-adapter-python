# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import tomllib
import importlib.util

here = path.abspath(path.dirname(__file__))

def _read_version():
    with open(path.join(here, "pyproject.toml"), "rb") as f:
        toml_data = tomllib.load(f)
    # PEP 621 location
    proj = toml_data.get("project", {})
    if "version" in proj:
        return proj["version"]
    raise RuntimeError("Version not found in pyproject.toml")


# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' in x]
__version__ = _read_version()

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

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
    long_description_content_type='text/markdown',
    url='https://github.com/cumulus-nasa/cumulus-message-adapter-python',  # Optional
    author='Cumulus Authors',  # Optional
    python_requires='>=3.12, <4.0',
    author_email='info@developmentseed.org',  # Optional
    classifiers=[  # Optional
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.12'
    ],
    keywords='nasa cumulus',  # Optional
    packages=find_packages(exclude=['.circleci', 'contrib', 'docs', 'tests']),
    py_modules=['run_cumulus_task', 'cumulus_logger'],
    install_requires=install_requires,
    dependency_links=dependency_links
)
