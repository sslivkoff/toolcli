import setuptools


setuptools.setup(
    name='toolcli',
    version='0.3.7',
    packages=setuptools.find_packages(),
    install_requires=[
        'ipdb',
        'rich',
        'typing_extensions',
    ],
)

