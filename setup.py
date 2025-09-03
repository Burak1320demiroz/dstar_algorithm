from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dstar-pathfinding",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="D* Star algorithm implementation for autonomous vehicle path planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dstar-pathfinding",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "pytest>=6.2.0",
        "networkx>=2.6",
    ],
    extras_require={
        "dev": ["pytest-cov", "black", "flake8"],
        "gui": ["pygame>=2.1.0"],
    },
)