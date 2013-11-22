from distutils.core import setup

setup(
    name='pylut',
    version='1.2.0',
    author='Greg Cotten',
    author_email='gcgc90@gmail.com',
    packages=['pylut'],
    scripts=['bin/basic_example.py'],
    url='http://pypi.python.org/pypi/PyLUT/',
    license='LICENSE.txt',
    description='Builds, modifies, visualizes, and converts 3D LUTs from popular .cube and .3dl formats.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy",
        "matplotlib"
    ],
)