import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='flippy',
    version='0.1',
    packages=['flippy'],
    include_package_data=True,
    license='ISC',
    description='A flexible feature flipper, simple to configure',
    long_description=README,
    url='https://github.com/kos/flippy/',
    author='Tomasz Wesołowski',
    author_email='kosashi@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "django",
        "dataclasses",
    ],
    extras_require={
        "test": [
            "pytest-django",
            "mockito",
            "mypy",
        ]
    }
)
