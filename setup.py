from setuptools import setup

with open('README', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='pipsi',
    version='0.6',
    description='Wraps pip and virtualenv to install scripts',
    long_description=readme,
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    url='http://github.com/mitsuhiko/pipsi/',
    py_modules=['pipsi'],
    install_requires=[
        'Click',
    ],
    entry_points='''
    [console_scripts]
    pipsi=pipsi:cli
    '''
)
