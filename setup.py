"""
Context Engineering: Beyond Prompt Engineering
A comprehensive framework for context design, orchestration, and optimization.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip()
            and not line.startswith("#")
            and not line.startswith("-")
        ]
else:
    requirements = []

# Development dependencies
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.4.0",
    "isort>=5.12.0",
    "pre-commit>=3.3.0",
    "ipdb>=0.13.13",
]

# Documentation dependencies
docs_requirements = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.2.0",
    "myst-parser>=2.0.0",
]

# Optional advanced features
extras_requirements = {
    "api": [
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    "distributed": [
        "redis>=4.5.0",
        "celery>=5.3.0",
    ],
    "all": [
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "redis>=4.5.0",
        "celery>=5.3.0",
    ],
}

setup(
    name="context-engineering",
    version="0.1.0",
    author="Context Engineering Contributors",
    author_email="",
    description="Context Engineering: Beyond Prompt Engineering - A comprehensive framework for LLM context optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidkimai/Context-Engineering",
    project_urls={
        "Bug Reports": "https://github.com/davidkimai/Context-Engineering/issues",
        "Source": "https://github.com/davidkimai/Context-Engineering",
        "Documentation": "https://github.com/davidkimai/Context-Engineering/tree/main/00_COURSE",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    keywords=[
        "context-engineering",
        "prompt-engineering",
        "llm",
        "large-language-models",
        "rag",
        "retrieval-augmented-generation",
        "ai",
        "machine-learning",
        "natural-language-processing",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        **extras_requirements,
        "dev": dev_requirements,
        "docs": docs_requirements,
    },
    entry_points={
        "console_scripts": [
            "context-eng=context_engineering.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "context_engineering": [
            "templates/*.yaml",
            "templates/*.json",
            "data/*.txt",
        ],
    },
    zip_safe=False,
)
