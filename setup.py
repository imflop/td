from setuptools import setup


setup(
    name="td",
    version="1.0.0",
    author="Oleg Makarov",
    author_email="imflop@gmail.com",
    url="https://github.com/imflop/td",
    install_requires=[
        "Click",
    ],
    py_modules=["td"],
    entry_points={
        "console_scripts": [
            "td=td:_main",
        ],
    },
)
