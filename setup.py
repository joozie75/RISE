from setuptools import setup, find_packages

setup(
    name='RISE_server',
    version='1.0',
    packages=['RISE_server'],
    include_package_data=True,
    package_data={
        'RISE_server': ['templates/classtable.html','templates/index.html', 'static/riselogo.png']
    },
    install_requires=[
        'flask',
        'argparse',
        'requests'
    ],
    author='jamesooi',
    author_email='',
    description='RISE flask web server'
)
