"""
CrosshairX — setup.py
Install with: pip install .
Or develop: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="crosshairx",
    version="1.0.0",
    description="GPU-Accelerated Custom Crosshair Overlay for Gaming (Roblox, FPS, etc.)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="CrosshairX Team",
    url="https://github.com/YOUR_USERNAME/crosshairx",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    entry_points={
        "console_scripts": [
            "crosshairx=crosshair_app.main:main",
        ],
        "gui_scripts": [
            "crosshairx-gui=crosshair_app.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
)
