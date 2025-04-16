from setuptools import setup, find_packages

setup(
    name="synthetic-healthcare-data",
    version="0.1.0",
    description="A synthetic healthcare data generator for RAG testing",
    author="Infanox",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "faker>=8.0.0",
        "python-dateutil>=2.8.0",
        "mimesis>=5.0.0",
        "scipy>=1.7.0",
        "tqdm>=4.60.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
)