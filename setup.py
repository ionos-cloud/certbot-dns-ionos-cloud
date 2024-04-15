from setuptools import setup
from setuptools import find_packages


install_requires = [
    "acme>=2.9.0",
    "certbot>=2.9.0",
    "setuptools",
    "requests",
    "mock",
]

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="certbot-dns-ionos",
    version="0.1.0",
    description="Certbot DNS Authenticator plugin for IONOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ionos-cloud/certbot-dns-ionos-cloud",
    author="IONOS Cloud DNS team",
    author_email="paas-dns@ionos.com",
    license="Apache License 2.0",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-ionos = certbot_dns_ionos.ionos:Authenticator"
        ]
    },
    test_suite="certbot-dns-ionos",
)