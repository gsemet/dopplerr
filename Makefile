.PHONY: build

DOCKER_BUILD?=docker build
TEST_PORT:=8086
SUBDLSRC_LANGUAGES?="fra,eng"

all: dev style checks build test-local
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

checks:
	pipenv run python setup.py sdist
	pipenv run python setup.py flake8
	pipenv run pylint --rcfile=setup.cfg --output-format=colorized dopplerr

build: readme
	@echo "Building..."
	@pipenv run python setup.py sdist bdist bdist_wheel

readme:
	@bash refresh_readme.sh

run-local:
	@echo "Running..."
	@pipenv run dopplerr --port $(TEST_PORT) --verbose --logfile "debug.log" --mapping tv=Series --languages $(SUBDLSRC_LANGUAGES)

shell:
	@echo "Shell"
	@pipenv shell

test-local:
	@pipenv run pytest dopplerr

test-docker:
	@echo "Testing docker build"
	@echo "You can change the default 'docker build' command line with the DOCKER_BUILD environment variable"
	@$(DOCKER_BUILD) -t dopplerr .

test-coverage:
	pipenv run py.test -v --cov dopplerr --cov-report term-missing

wheels:
	@echo "Creating distribution wheel"
	@pipenv run python setup.py bdist_wheel

pypi-publish: wheels
	@echo "Publishing to Pypy"
	@pipenv run python setup.py sdist bdist upload -r pypi

update:
	@echo "Updating dependencies..."
	@pipenv update

githook:style readme

push: githook
	git push

wheel: wheels
pypi: pypi-publish
develop: dev
devel: dev
install: install-system
run: run-local
check: checks
docker: test-docker
styles: style
