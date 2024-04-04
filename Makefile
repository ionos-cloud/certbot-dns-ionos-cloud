test:
	python -m unittest

lint:
	python -m mypy .
	python -m flake8 .