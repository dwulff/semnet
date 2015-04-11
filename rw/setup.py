# used to build Cython genz

from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize("genz.pyx"),
    include_dirs=[numpy.get_include()]
)
