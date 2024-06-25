from setuptools import find_packages, setup


def read_requirements():
    with open("requirements.txt") as req_file:
        requirements = req_file.read().splitlines()
        # Filter out local package references and comments
        return [
            req
            for req in requirements
            if req and not req.startswith("-e ") and not req.startswith("#")
        ]


setup(
    name="basket_viz",
    version="0.1.3",
    packages=find_packages(),
    description="A Python library for creating interactive and customizable visualizations of basketball statistics.",
    author="basket-viz",
    author_email="basketviz@gmail.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sVujke/basket-viz",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license="MIT",
    install_requires=read_requirements(),
)
