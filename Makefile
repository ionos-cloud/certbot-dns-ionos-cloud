test:
	python -m unittest

lint:
	python -m mypy certbot_dns_ionos/
	python -m flake8  --max-line-length 90 certbot_dns_ionos/