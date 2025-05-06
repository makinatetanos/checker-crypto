from setuptools import setup, find_packages

setup(
    name="verificador-monero",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "PyQt6>=6.6.1",
        "python-dotenv>=1.0.0",
        "cryptography>=42.0.2",
        "monero>=0.8.2",  # Cambiado de monero-python-rpc a monero
        "base58>=2.1.1",
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'pytest-qt>=4.4.0',
            'pytest-xvfb>=3.0.0',
            'coverage>=7.5.0',
        ],
    },
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Verificador de wallets Monero perdidas",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/verificador-monero",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "verificador-monero=src.verificador_monero.main:main",  # Corregido para reflejar la estructura src/
        ],
    },
)