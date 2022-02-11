import setuptools


setuptools.setup(
    name='toolcli',
    version='0.1.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'ipdb',
        'rich',
        'typing_extensions',
    ],
)

