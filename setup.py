#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import sys

# Ensure we're on macOS with Apple Silicon
if sys.platform != 'darwin':
    raise RuntimeError("This package is designed for macOS with Apple Silicon only")

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mlx-llm-controller",
    version="1.0.0",
    author="MLX LLM Controller Team",
    author_email="contact@example.com",
    description="MLX Large Language Model controller with precision parameter tuning and GPU optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mlx-llm-controller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "mlx-llm-controller=start_mlx_frontend:main",
            "mlx-optimize=scripts.optimize_mlx_gpu:main",
            "mlx-download=scripts.download_model:main",
        ],
    },
    package_data={
        "": ["*.html", "*.js", "*.css", "*.command"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="mlx llm apple-silicon metal gpu-optimization mcp model-context-protocol",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mlx-llm-controller/issues",
        "Source": "https://github.com/yourusername/mlx-llm-controller",
        "Documentation": "https://github.com/yourusername/mlx-llm-controller#readme",
        "MCP Integration": "https://github.com/modelcontextprotocol",
    },
)