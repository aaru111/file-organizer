from setuptools import setup, find_packages

setup(
    name='file-organizer',  # Name of your package
    version='1.0.0',  # Version of your package
    author='Your Name',  # Replace with your name
    author_email='your.email@example.com',  # Replace with your email
    description='A versatile file organization tool with both CLI and GUI interfaces.',
    long_description=open('README.md').read(),  # This will be displayed on PyPI
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/file-organizer',  # Replace with your GitHub repo URL
    packages=find_packages(include=['modules', 'modules.*']),  # Automatically find packages in modules folder
    include_package_data=True,
    install_requires=[
        'prompt-toolkit==3.0.38',
        'colorama==0.4.6',
        'rich'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Minimum Python version required
    entry_points={
        'console_scripts': [
            'file-organizer=main:main',  # This allows running `file-organizer` from command line
        ],
    },
)
