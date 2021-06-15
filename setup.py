from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='MARS',
    url='https://github.com/bhelsel/MARS',
    author='Brian Helsel',
    author_email='bhelsel80@gmail.com',
    # Needed to actually package something
    packages=['MARS'],
    # Needed for dependencies
    install_requires=['numpy', 'pandas', 'datetime', 'os'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)