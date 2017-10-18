from setuptools import setup, find_packages


setup(
    name='wolfquant',
    version='0.0.0',
    description='构建期货交易的框架',
    packages=find_packages(exclude=[]),
    author='rickyall',
    author_email='rickyallqi@gmail.com',
    package_data={'': ['*.*']},
    url='https://github.com/rickyall/wolfquant.git',
)
