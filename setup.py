from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.8'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='django-merlin',
    version=version,
    description="Providing alternate form wizards for the Django project.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      'Development Status :: 4 - Beta',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python :: 2.7'
    ],
    keywords='forms wizard django session',
    author='supercodepoet',
    author_email='travis@travischase.me',
    url='http://github.com/supercodepoet/django-merlin',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires
)
