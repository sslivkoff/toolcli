import setuptools


setuptools.setup(
    name='toolcli',
    version='0.3.9',
    packages=setuptools.find_packages(),
    install_requires=[
        'ipdb',
        'rich',
        'typing_extensions',
    ],
)

