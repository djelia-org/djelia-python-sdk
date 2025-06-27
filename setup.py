import os

from setuptools import find_packages, setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="djelia",
    version="1.1.1",
    author="Djelia",
    author_email="support@djelia.cloud",
    description="Djelia Python SDK - Advanced AI for African Languages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djelia-org/djelia-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/djelia-org/djelia-python-sdk/issues",
        "Documentation": "https://djelia.cloud/docs",
        "Source Code": "https://github.com/djelia-org/djelia-python-sdk",
        "Homepage": "https://djelia.cloud",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "pydantic-settings>=2.10.1",
        "pydantic>=2.7.0",
        "tenacity>=9.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "isort>=5.0.0",
            "ruff>=0.11.4",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "python-dotenv>=0.19.0",
        ],
    },
    keywords=[
        "djelia",
        "nlp",
        "translation",
        "transcription",
        "text-to-speech",
        "tts",
        "african languages",
        "bambara",
        "mali",
        "async",
        "ai",
        "machine learning",
        "speech recognition",
        "voice synthesis",
        "multilingual",
        "linguistics",
    ],
    include_package_data=True,
    zip_safe=False,
)
