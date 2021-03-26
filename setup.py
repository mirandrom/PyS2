from setuptools import setup, find_packages
import pathlib
import re

here = pathlib.Path(__file__).parent.resolve()
readme = (here / "README.md").read_text(encoding="utf-8")
version = re.search(
    '__version__ = "([^"]+)"',
    (here / "s2/__init__.py").read_text(encoding="utf-8")
).group(1)

setup(
    name="pys2",
    version=version,
    author="mirandrom",
    description=("PyS2  is a python wrapper for the Semantic Scholar (S2) API"),

    long_description_content_type="text/markdown",
    long_description=readme,
    keywords="semantic scholar, s2, scientific literature, citation graph",
    url="https://github.com/mirandrom/pys2/",
    project_urls={ 
        "Bug Reports": "https://github.com/mirandrom/pys2/issues",
        "Source": "https://github.com/mirandrom/pys2/",
        "Docs": "https://pys2.readthedocs.org/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],

    python_requires=">=3.6, <4",
    install_requires=[
        "requests >=2.6, <3.0",
        "pydantic >=1.8, < 2.0",
    ],
    extras_require={
        "readthedocs": ["sphinx>=3, <4.0"],
        "test": [
            "betamax >=0.8, <0.9",
            "pytest >=6, <7",
        ],
    },
    packages=find_packages(include=["s2","s2.*"]),
)