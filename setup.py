from setuptools import setup, find_packages

setup(
    name='carmacs_tools',
    version='0.1',
    url='https://github.com/carmacs2023/carmacs_tools',
    license='MIT',
    author='carmacs',
    author_email='carmacs@gmail.com',
    description='Generic tools used by other repositories, updated independently',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(where="src"),  # Tells setuptools to look for packages in the src directory
    package_dir={"": "src"},  # Tells setuptools that package sources are under src
    install_requires=[      # Specify package outside standard libraries included in Python
        'pandas>=1.0',      # Specify versions if needed, means version 1 or higher
        'requests>=2.0'     # Specify versions if needed, means version 2 or higher
        'rapidfuzz>=3.8'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: MIT License',
        'Environment :: Console',  # Indicates that this package is suitable for console environments
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    entry_points={
        'console_scripts': [
            'ct=cli:main'
        ]
    },
)
