![Release](https://img.shields.io/github/v/release/ionos-cloud/certbot-dns-ionos-cloud.svg)
[![PyPI version](https://img.shields.io/pypi/v/ionoscloud-dns)](https://pypi.org/project/certbot-dns-ionos-cloud/)

![Alt text](https://raw.githubusercontent.com/ionos-cloud/certbot-dns-ionos-cloud/main/.github/IONOS.CLOUD.BLU.svg)

# IONOS Cloud DNS Certbot Authenticator Plugin

The IONOS Cloud DNS Certbot Plugin automates SSL/TLS certificate creation for [IONOS Cloud](https://cloud.ionos.com/) zones. It implements the [Authenticator](https://github.com/certbot/certbot/blob/master/certbot/certbot/interfaces.py#L158) interface which is used by Certbot to perform a [DNS-01](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) challenge.

## Requirements

To make use of the plugin, the following is needed:
* an [IONOS Cloud](https://cloud.ionos.com/) account
* an access token (a token can be obtained from the [DCD](https://dcd.ionos.com/) token manager or through the [Authentication API](https://api.ionos.com/docs/authentication/v1/))


## Installation

```
pip install certbot-dns-ionos
```

## Arguments

| Argument                            | Example     | Description                                                                                                                                                                     |
|-------------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--authenticator`                   | dns-ionos       | Tells certbot which plugin to use. `dns-ionos` should be used for this plugin.                                                                               | 
| `--dns-ionos-credentials`         | ./credentials.ini | Denotes the directory path to the credentials file. Required. |
| `--dns-ionos-propagation-seconds` | 120               | Configures the duration in seconds that certbot waits before querying the TXT record. (Default: 120)                                  |


## Credentials file

As mentionned in the previous section, the `--dns-ionos-credentials` needs to point to an ini file containing the IONOS API access token. The file must contain the `ionos_dns_token` key with the value of the access token. 

```
dns_ionos_token=YOUR_API_JWT_ACCESS_TOKEN

```

## Example Usage

```
certbot certonly \
  --authenticator dns-ionos \
  --dns-ionos-credentials /path/to/credentials.ini \
  --dns-ionos-propagation-seconds 60 \
  --agree-tos \
  --rsa-key-size 4096 \
  -d 'example.com' \
  -d '*.example.com'
```

In the background, the plugin will try to find your zone. If found, it will create a TXT record for the [DNS-01](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) challenge. At the end of the process, the TLS/SSL certificate is generated and the TXT record is deleted.

## Support

If you encounter any issues or have suggestions, please feel free to open an [issue](https://github.com/ionos-cloud/certbot-dns-ionos-cloud/issues).

## License

This project is licensed under the Apache License 2.0 License - see the [LICENSE](https://github.com/ionos-cloud/certbot-dns-ionos-cloud/blob/init/LICENSE) file for details.

## How to develop locally

To develop and test the plugin locally, it is recommend to create a python [virtual environment](https://docs.python.org/3/library/venv.html). For example: `python -m venv .venv`

After activating the virtual environment, the following command should be used to install the project to the virtual environment local site packages: `pip install -e .`

Afterwards, any changes made to the plugin will be directly reflected when executing the `certbot certonly --authenticator dns-ionos` (without the need to execute `pip install` again). 

It's important to note that the following arguments need also to be provided when developing locally in a virtual environment `--logs-dir`, `--config-dir`, `--work-dir`, otherwise the `certbot` will attempt to use the global folders for logging, configuration, and work. This may not work because of the lack of permissions, so you may see errors like below if those arguments are not set:

```
The following error was encountered:
[Errno 13] Permission denied: '/var/log/letsencrypt/.certbot.lock'
Either run as root, or set --config-dir, --work-dir, and --logs-dir to writeable paths.
```

As explained by the error message, to be able write to `/var/log/letsencrypt/`, root permissions are needed. However, when running as a root (e.g `sudo certbot`), the global `certbot` package will be used and not the one from the virtual environment. The solution is to set `--logs-dir`, `--config-dir`, and `--work-dir` to a different folder for which the current user has write permissions.

## Testing

unit tests can be run using: `make test`

## Related Plugins

It's important to note that this plugin targets IONOS [Cloud DNS service](https://cloud.ionos.com/network/cloud-dns). 
IONOS offers a different service for managing DNS zones, refered to as [IONOS Developer DNS API](https://developer.hosting.ionos.com/docs/dns). For the latter, there is dedicated plugin managed by the community: [https://github.com/helgeerbe/certbot-dns-ionos](https://github.com/helgeerbe/certbot-dns-ionos)
