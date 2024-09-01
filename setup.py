from setuptools import setup, find_packages

setup(
    name='file-organizer',  
    version='1.0.0',  
    author='Aarav',  
    author_email='aarav12303@gmail.com',  
    description='A versatile file organization tool with both CLI and GUI interfaces.',
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',
    url='https://github.com/aaru111/file-organizer', 
    packages=find_packages(include=['modules', 'modules.*']),
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
    python_requires='>=3.7', 
    entry_points={
        'console_scripts': [
            'file-organizer=main:main',  
        ],
    },
)
