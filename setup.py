from setuptools import setup, find_packages

setup(
    name='audio-fingerprinting',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'click==8.1.3',
        'numpy==1.22.4',
        'librosa==0.9.1',
        'python-dotenv==0.20.0',
        'pyyaml==6.0',
        'sqlalchemy==1.4.36'
    ],
    entry_points={
        'console_scripts': [
            'audio-fingerprint=scripts.cli:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='An advanced audio fingerprinting system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/audio-fingerprinting',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)