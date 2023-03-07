from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="rss_reader",
    version="4.0",
    author="Pavel Saiko",
    author_email="3859615@gmail.com",
    description=("RSS reader is a command-line utility which "
                 "receives RSS URL and prints results in human-readable format."),
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["fb2", "pathlib", "wheel", "docutils", "requests", "bs4", "python-dateutil", "lxml", "html5lib"],
    entry_points={"console_scripts": ["rss_reader=package:main"]}
)

