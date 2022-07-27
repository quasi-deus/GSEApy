#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib
import re
import sys

from setuptools import setup
from setuptools.command.sdist import sdist as SdistCommand
from setuptools.command.test import test as TestCommand

# If could not build wheels for gseapy which use PEP 517 and cannot be installed directly 
# need: pip install --upgrade pip setuptools wheel
# or conda update setuptools wheel

try:
    from setuptools_rust import RustExtension
except ImportError:
    import subprocess

    errno = subprocess.call([sys.executable, "-m", "pip", "install", "setuptools-rust"])
    if errno:
        print("Please install setuptools-rust package")
        raise SystemExit(errno)
    else:
        from setuptools_rust import RustExtension



def find_version():
    filepath = os.path.join("gseapy", "__main__.py")
    with open(os.path.join(os.path.dirname(__file__), filepath), encoding="utf8") as fp:
        content = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


__author__ = "Zhuoqing Fang"
__version__ = find_version()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


class CargoModifiedSdist(SdistCommand):
    def make_release_tree(self, base_dir, files):
        """Stages the files to be included in archives"""
        files.append("Cargo.toml")
        files += [str(f) for f in pathlib.Path("src").glob("**/*.rs") if f.is_file()]
        super().make_release_tree(base_dir, files)


def readme():
    with open("README.rst") as f:
        return f.read()

setup(name='gseapy',
      version=__version__,
      description='Gene Set Enrichment Analysis in Python',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Software Development :: Libraries'],
      keywords= ['Gene Ontology', 'GO','Biology', 'Enrichment',
          'Bioinformatics', 'Computational Biology',],
      url='https://github.com/zqfang/gseapy',
      author= __author__,
      author_email='fzq518@gmail.com',
      license='MIT',
      packages=['gseapy'],
      #package_data={'gseapy': ["data/*.txt"],},
      #include_package_data=True,
      setup_requires = ["setuptools-rust>=0.10.1", "wheel"],
      install_requires=[
                        'numpy>=1.13.0',
                        'scipy',
                        'pandas',
                        'matplotlib',
                        'bioservices',
                        'requests',
                        'joblib'],
      rust_extensions=[RustExtension("gseapy.gse", "Cargo.toml",  debug="DEBUG" in os.environ)], #  binding=Binding.RustCPython
      entry_points={'console_scripts': ['gseapy = gseapy.__main__:main'],},
      tests_require=['pytest'],
      cmdclass = {"test": PyTest, "sdist": CargoModifiedSdist},
      zip_safe=False, # Rust extensions are not zip safe
      download_url='https://github.com/zqfang/gseapy',)
