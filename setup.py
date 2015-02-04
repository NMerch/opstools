from distutils.core import setup

setup(
    name='opstools',
    version='1.0',
    description="AWS Provisioning and bootstrapping utility",
    packages=['opstools'],
    author='Nadir Merchant',
    author_email='nadir.merchant@mobidia.com',
    install_requires=['boto']
)
