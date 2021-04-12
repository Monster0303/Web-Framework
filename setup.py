from setuptools import setup


setup(
    name="web-framework",
    version="0.0.1",
    author="monster",
    description="This is like Flask Web.",
    packages=['web'],
    python_requires='>=3.8',
    install_requires="webob>=1.8.6"
)
