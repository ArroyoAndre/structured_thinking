import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="structured_thinking",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Utilities for structured thinking and problem-solving",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YourUser/structured_thinking",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)