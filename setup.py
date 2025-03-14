from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = ""#fh.read()

setup(
    name="djelia",
    version="0.1.0",
    author="Djelia",
    author_email="support@djelia.com",
    description="Python SDK for the Djelia API, providing access to linguistic models for African languages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djelia-org/djelia-python-client",
    
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="djelia, nlp, translation, transcription, text-to-speech, african languages, bambara, mali",
    project_urls={
        "Documentation": "https://djelia.cloud/docs",
        "Bug Tracker": "https://github.com/djelia-org/djelia-python-client/issues",
    },
)