from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pynubank_wrapper",
    version="0.0.1",
    author="Bruno Anhaia",
    author_email="hiroki.zx@gmail.com",
    description="A wrapper package built over pynubank",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pynubank'],
    url="https://bitbucket.org/zeta-tech/budget-planner/",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
