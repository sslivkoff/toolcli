import setuptools


setuptools.setup(
    name='toolcli',
    version='0.3.10',
    packages=setuptools.find_packages(),
    install_requires=[
        'rich>=12.1.0',
        'typing_extensions>=0.4.0',
    ],
    extras_require={
        'full': [
            'ipdb',
        ],
    },
)
