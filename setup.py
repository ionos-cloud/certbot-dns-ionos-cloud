from setuptools import setup
from setuptools import find_packages


install_requires = [
    "acme>=2.9.0",
    "certbot>=2.9.0",
    "setuptools",
    "requests",
    "mock",
]


setup(
    name="certbot-dns-ionos",
    version="0.1.0",
    description="Certbot DNS Authenticator plugin for IONOS",
    url="https://github.com/ionos-cloud/certbot-dns-ionos-plugin",
    author="IONOS Cloud DNS team",
    author_email="paas-dns@ionos.com",
    license="Apache License 2.0",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[],
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