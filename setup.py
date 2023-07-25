from setuptools import setup, find_packages


setup(
    name='SGZ',
    version='0.1.0',
    python_requires='==2.7.6',
    packages=find_packages(),
    install_requires = [
        'pillow', 
        'ipykernel',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'tqdm',
        'backports.functools-lru-cache',
        'setuptools'
    ]
)