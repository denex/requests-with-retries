import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='requests-with-retries',
    version='0.0.1',
    author='Denis Averin',

    description='Wrapper around requests',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/denex/requests-with-retries',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    requires=[
        'requests',
    ]
)
