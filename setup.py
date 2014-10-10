import os
from setuptools import setup, find_packages
 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
setup(
    name = "django-voting",
    version = "0.1",
    url = 'http://github.com/scottwrobinson/django-voting',
    license = 'BSD',
    description = "Django voting application that tracks the number of votes for any DB objects.",
    long_description = read('README.md'),
 
    author = 'Scott Robinson',
 
    packages = find_packages(),
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
