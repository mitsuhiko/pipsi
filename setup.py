import sys
from setuptools import setup


with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')


requires = [
    'Click'
]


if sys.version_info.major == 2:
    requires.extend([
        'virtualenv'
    ])


setup(
    name='pipsi',
    version='0.10.dev',
    description='Wraps pip and virtualenv to install scripts',
    long_description=readme,
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    url='http://github.com/mitsuhiko/pipsi/',
    packages=['pipsi'],
    package_data={
        'pipsi': ['scripts/*.py'],
    },
    include_package_data=True,
    install_requires=requires,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points='''
    [console_scripts]
    pipsi=pipsi:cli
    '''
)
