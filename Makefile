#### build

#### deploy

####  start at local for debug

start-spring-webmvc-local:
	@:

### setup environment for local

init-python:
	python -m pip install pipenv
	@if [ -z "$(python -m pip list --disable-pip-version-check | grep pyenv)" ]; then \
		curl https://pyenv.run | bash \
	fi

test:
	python -m pytest

doc:
	python -m pydoc -b

style: black flake8

flake8:
	python -m flake8

black:
	python -m black --line-length 79 --target-version=py37 --check ./	

install:
	pipenv install --dev

shell:
	pipenv shell

clean:
	find . -name "*.py[co]" -delete
	find . -name "*~" -delete
	find . -name "__pycache__" -delete

uninstall:
	pipenv clean
	pipenv --rm
	rm -rf ~/.pyenv
	pip3 uninstall pipenv
