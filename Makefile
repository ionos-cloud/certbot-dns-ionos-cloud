test:
	python -m unittest

lint:
	python -m mypy .
	python -m flake8  --max-line-length 90 .