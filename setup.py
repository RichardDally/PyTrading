import setuptools


with open("readme.md", "r") as fh:
    long_description = fh.read()


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setuptools.setup(
    author="Richard Dally",
    name="pytrading",
    version="1.0.0",
    description="Start your own financial market at home",
    url="https://github.com/RichardDally/PyTrading",
    license="GPLv3",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.11",
)
