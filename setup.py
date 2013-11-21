from distutils.core import setup

setup(
    name='pylut',
    version='1.0.0',
    author='Greg Cotten',
    author_email='gcgc90@gmail.com',
    packages=['pylut'],
    scripts=['bin/basic_example.py'],
    url='http://pypi.python.org/pypi/PyLUT/',
    license='LICENSE.txt',
    description='Manipulates 3D LUTs',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy"
    ],
)