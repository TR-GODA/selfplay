import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="selfplay",  # Replace with your own username
    version="1.0.1",
    author="Doğukan Arslan",
    author_email="dogukan997@hotmail.com",
    description="A python module for automatic chatbot training data creation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
