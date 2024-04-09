LINE_LENGTH=90

test:
	python -m unittest

lint:
	python -m mypy certbot_dns_ionos/
	python -m flake8  --max-line-length $(LINE_LENGTH) certbot_dns_ionos/

format:
	python -m black -l $(LINE_LENGTH) certbot_dns_ionos/

install-ci-dependencies:
	pip install -r ci-requirements.txt

install-module-dependencies:
	pip install -r requirements.txt

install-dependencies: install-ci-dependencies install-module-dependencies