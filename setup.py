from setuptools import setup, find_namespace_packages

with open('README.md') as f:
    README = f.read()

with open('requirements.txt') as f:
    REQUIREMENTS = f.read()

setup(
    name='franklin_toolkit',
    version='1.0.0',
    author='Franklin Team',
    description='Franklin toolkit',
    long_description=README,
    install_requires=REQUIREMENTS,
    packages=find_namespace_packages(include=['franklin*'])
)