.PHONY: build

DOCKER_BUILD?=docker build
TEST_PORT:=8086
SUBDLSRC_LANGUAGES?="fra,eng"

all: dev style checks build dists test-unit
dev:
	@echo "Setting up development environment"
	@pipenv install --dev

install-local:
	@pipenv install

install-system:
	@pipenv install --system

style:
	@echo "Formatting python files..."
	@pipenv run isort -y
	@pipenv run autopep8 --in-place --recursive setup.py dopplerr
	@pipenv run yapf --recursive -i dopplerr

checks: sdist flake8 pylint

flake8:
	pipenv run python setup.py flake8

pylint:
	pipenv run pylint --rcfile=.pylintrc --output-format=colorized dopplerr

build: readme
	@echo "Building..."
	@pipenv run python setup.py sdist bdist bdist_wheel

readme:
	@bash refresh_readme.sh

run-local:
	@echo "Starting Dopplerr on http://localhost:$(TEST_PORT) ..."
	@pipenv run dopplerr --port $(TEST_PORT) --verbose --logfile "debug.log" --mapping tv=Series --languages $(SUBDLSRC_LANGUAGES)

shell:
	@echo "Shell"
	@pipenv shell

test-unit:
	@pipenv run pytest dopplerr

test-docker:
	@echo "Testing docker build"
	@echo "You can change the default 'docker build' command line with the DOCKER_BUILD environment variable"
	@$(DOCKER_BUILD) -t dopplerr .

test-coverage:
	pipenv run py.test -v --cov dopplerr --cov-report term-missing

dists: sdist bdist wheels

sdist:
	pipenv run python setup.py sdist

bdist:
	pipenv run python setup.py bdist

wheels:
	@echo "Creating distribution wheel"
	@pipenv run python setup.py bdist_wheel

pypi-publish: sdist bdist wheels
	@echo "Publishing to Pypy"
	@pipenv run python setup.py upload -r pypi

update:
	@echo "Updating dependencies..."
	@pipenv update

githook:style readme

push: githook
	git push

# aliases to gracefully handle typos on poor dev's terminal
check: checks
devel: dev
develop: dev
dist: dists
docker: test-docker
install: install-system
pypi: pypi-publish
run: run-local
styles: style
test: test-unit
wheel: wheels
