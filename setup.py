from setuptools import setup, find_packages


setup(
    name='Snooper',
    version="0.1",
    packages=find_packages(),
    author="zackey-heuristics",
    install_requires=["langdetect", "praw"],
    description="Output the snooper results in JSON format",
    include_package_data=True,
    url='https://github.com/zackey-heuristics/Snooper',
    py_modules=["snooper", "snooper_json_output"],
    entry_points={
        "console_scripts": [
            "snooper-json = snooper_json_output:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
)