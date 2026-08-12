![Release](https://img.shields.io/github/v/release/ionos-cloud/certbot-dns-ionos-cloud.svg)
[![PyPI version](https://img.shields.io/pypi/v/certbot-dns-ionos-cloud)](https://pypi.org/project/certbot-dns-ionos-cloud/)

![Alt text](https://raw.githubusercontent.com/ionos-cloud/certbot-dns-ionos-cloud/main/.github/IONOS.CLOUD.BLU.svg)

# IONOS Cloud DNS Certbot Authenticator Plugin

The IONOS Cloud DNS Certbot Plugin automates SSL/TLS certificate creation for [IONOS Cloud](https://cloud.ionos.com/) zones. It implements the [Authenticator](https://github.com/certbot/certbot/blob/master/certbot/certbot/interfaces.py#L158) interface which is used by Certbot to perform a [DNS-01](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) challenge.

## Requirements

To make use of the plugin, the following is needed:
* an [IONOS Cloud](https://cloud.ionos.com/) account
* an access token (a token can be obtained from the [DCD](https://dcd.ionos.com/) token manager or through the [Authentication API](https://api.ionos.com/docs/authentication/v1/))

## Authentication Methods

Both username/password and token authentication are supported. The username/password method has the advantage of not requiring the user to intervene periodically. If a token is used, it falls under the responsibility of the user to renew the token periodically (IONOS tokens can have a maximum ttl of 365 days). Regardless of the method used, it is highly recommended to scope the privileges to the DNS management only. This can be done by creating a new IAM user under your main contract, and scoping the privileges to "Access and manage DNS". More details on how to create a bot user can be found [here](https://github.com/ionos-cloud/cert-manager-webhook-ionos-cloud/blob/main/docs/create-bot-user.md)

> [!IMPORTANT]  
> It is not recommended to use the credentials of the root/Admin account. 

## Installation

```
pip install certbot-dns-ionos-cloud
```

## Arguments

| Argument                            | Example     | Description                                                                                                                                                                     |
|-------------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--authenticator`                   | dns-ionos-cloud      | Tells certbot which plugin to use. `dns-ionos` should be used for this plugin.                                                                               | 
| `--dns-ionos-cloud-credentials`         | ./credentials.ini | Denotes the directory path to the credentials file. Required. |
| `--dns-ionos-cloud-propagation-seconds` | 120               | Configures the duration in seconds that certbot waits before querying the TXT record. (Default: 120)                                  |

## Credentials file

As mentioned in the previous section, the `--dns-ionos-cloud-credentials` needs to point to an ini file containing the IONOS API access token. The file must contain either the `ionos_dns_cloud_token` key with the value of the access token or the keys `ionos_dns_cloud_username`, `ionos_dns_cloud_password` with the values of the bot username and password, respectively. 

```
ionos_dns_cloud_token=YOUR_API_JWT_ACCESS_TOKEN
ionos_dns_cloud_username=THE_BOT_ACCOUNT_USERNAME
ionos_dns_cloud_password=THE_BOT_ACCOUNT_PASSWORD
```

## Example Usage

```
certbot certonly \
  --authenticator dns-ionos-cloud \
  --dns-ionos-cloud-credentials /path/to/credentials.ini \
  --dns-ionos-cloud-propagation-seconds 60 \
  --agree-tos \
  --rsa-key-size 4096 \
  -d 'example.com'
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
IONOS offers a different service for managing DNS zones, referred to as [IONOS Developer DNS API](https://developer.hosting.ionos.com/docs/dns). For the latter, there is dedicated plugin managed by the community: [https://github.com/helgeerbe/certbot-dns-ionos](https://github.com/helgeerbe/certbot-dns-ionos)
