from setuptools import setup, find_packages

setup(
    name="software-monitor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.1",
        "requests>=2.31.0",
        "packaging>=23.2",
    ],
    entry_points={
        'console_scripts': [
            'software-monitor=software_monitor.main:main',
        ],
    },
    author="Your Name",
    description="Ein Tool zum Überwachen von Software-Updates",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="software, updates, monitor",
    python_requires=">=3.8",
)
