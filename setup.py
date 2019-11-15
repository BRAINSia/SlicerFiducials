import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slicerfiducials",
    version="0.1.1",
    author="abpwrs & ArjitJ",
    author_email="alexander-powers@uiowa.edu",
    description="A small package for slicer fiducial manipulation and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abpwrs/slicerfiducials",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'itk','pandas','numpy',
      ],
    python_requires=">=3.6",
)
