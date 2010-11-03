from setuptools import setup, find_packages

setup(
    name = "twisted-smpp",
    version = "0.1",
    url = 'http://github.com/dmaclay/twisted-smpp',
    license = 'BSD',
    description = "Twisted SMPP Library",
    author = 'David Maclay',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = [],
)

