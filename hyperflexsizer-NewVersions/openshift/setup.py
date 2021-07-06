import os

# Put here required packages
packages = ['Django==1.7.0','MySQL-python','djoser==0.3.0', 'djangorestframework==3.1.1', 'django-rest-swagger==0.3.4', 'pulp', 'reportlab', 'requests', 'jsonfield==1.0.3', 'mailer', 'Pillow==2.6.1', 'python-pptx==0.6.11', 'python-ldap==2.4.38', 'wget', 'xlrd==1.0.0', 'packaging', 'matplotlib==2.1.0']

setup(name='hyperflexsizer',
      version='1.0',
      description='OpenShift App',
      author='Your Name',
      author_email='example@example.com',
      url='https://pypi.python.org/pypi',
      install_requires=packages,
)
