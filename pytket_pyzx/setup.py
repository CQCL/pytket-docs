import setuptools
from setuptools import setup

def find_pytket_subpackages():
    locations = [('pytket', 'pytket')]
    pkg_list = []

    for location, prefix in locations:
        pkg_list += list(
            map(lambda package_name: '{}.{}'.format(prefix, package_name),
                setuptools.find_packages(where=location))
        )

    return pkg_list

setup(
    name='pytket_pyzx',
    version='0.1.2',
    author='Alexander Cowtan',
    author_email='alexander.cowtan@cambridgequantum.com',
    python_requires='>=3.6',
    url='https://github.com/CQCL/pytket',
    description='Extension for pytket, providing translation to and from the PyZX framework',
    long_description= open('README.md').read(),
    license='Apache 2.0',
    packages = find_pytket_subpackages(),
    install_requires = [
        'pytket >=0.2.0'
        #also requires pyzx, but this can only be got from source on github (https://github.com/Quantomatic/pyzx)
    ],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering"
    ],
    zip_safe=False
)