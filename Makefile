.PHONY: build

MODULE:=dopplerr
DOCKER_BUILD?=docker build
PORT:=8086
LANGUAGES?=fra,eng
BASEDIR?=/
MAPPING?=tv=Series
OPENSUBTITLES_USERNAME?=username
OPENSUBTITLES_PASSWORD?=password

all: dev version style checks frontend-build build dists docker test-unit
all-frontend: frontend-dev frontend-build
all-local: dev style checks dists test-unit
all-docker: dev style checks docker test-unit

release: build

bootstrap:
	@echo "Please sudo the following command in your environment:"
	@echo "  sudo -E ./bootstrap-system.sh"
	@echo "  sudo -E ./setup-pip.sh"

dev:
	@echo "Setting up development environment"
	pipenv install --dev --three

frontend-dev:
	cd frontend ; make dev

frontend-build:
	cd frontend ; make build

frontend-run:
	cd frontend ; make run

version:
	cd frontend ; make release

install-local:
	pipenv install

install-system:
	pipenv install --system

style: isort autopep8 yapf

isort:
	pipenv run isort -y

autopep8:
	pipenv run autopep8 --in-place --recursive setup.py $(MODULE)

yapf:
	pipenv run yapf --style .yapf --recursive -i $(MODULE)

checks: flake8 pylint

flake8:
	pipenv run python setup.py flake8

pylint:
	pipenv run pylint --rcfile=.pylintrc --output-format=colorized $(MODULE)

build: readme version dists

readme:
    # Only for Pypi, which does not render MarkDown Readme
	pandoc --from=markdown --to=rst --output=README.rst README.md

run-local:
	@echo "Starting Dopplerr on http://localhost:$(PORT) ..."
	pipenv run $(MODULE) \
	           --port $(PORT) \
			   --verbose \
			   --logfile "debug.log" \
			   --mapping $(MAPPING) \
			   --languages $(LANGUAGES) \
			   --basedir $(BASEDIR) \
			   --opensubtitles $(OPENSUBTITLES_USERNAME) $(OPENSUBTITLES_PASSWORD) \
			   --frontend frontend/dist

run-local-env:
	@echo "Starting Dopplerr on http://localhost:$(PORT) using environment variable parameters..."
	DOPPLERR_PORT=$(PORT) \
		DOPPLERR_MAPPING="$(MAPPING)" \
		DOPPLERR_LANGUAGES=$(LANGUAGES) \
		DOPPLERR_BASEDIR=$(BASEDIR) \
		DOPPLERR_OPENSUBTITLES_USERNAME=$(OPENSUBTITLES_USERNAME) \
		DOPPLERR_OPENSUBTITLES_PASSWORD=$(OPENSUBTITLES_PASSWORD) \
		pipenv run $(MODULE) \
			--verbose \
			--logfile "debug.log" \
			--frontend frontend/dist

run-docker: kill-docker
	docker run -p $(PORT):$(PORT) \
			   -e "DOPPLERR_LANGUAGES=$(LANGUAGES)" \
			   -e "DOPPLERR_MAPPING='$(MAPPING)'" \
			   -e "DOPPLERR_LOGFILE=debug.log" \
			   -e "DOPPLERR_BASEDIR=$(BASEDIR)" \
			   -e "DOPPLERR_OPENSUBTITLES_USERNAME=$(OPENSUBTITLES_USERNAME)" \
			   -e "DOPPLERR_OPENSUBTITLES_PASSWORD=$(OPENSUBTITLES_PASSWORD)" \
			   -t dopplerr:latest

run_frontend:
	cd frontend ; make run

kill-docker:
	docker kill $$(docker ps --format '{{.Names}}\t{{.Image}}\t' | grep dopplerr | cut -f1)

shell:
	@echo "Shell"
	pipenv shell

test-unit:
	pipenv run pytest $(MODULE)

docker-build:
	@echo "Testing docker build"
	@echo "You can change the default 'docker build' command line with the DOCKER_BUILD environment variable"
	$(DOCKER_BUILD) -t $(MODULE) .

test-coverage:
	pipenv run py.test -v --cov ./ --cov-report term-missing

dists: sdist bdist wheels

sdist:
	pipenv run python setup.py sdist

bdist:
	pipenv run python setup.py bdist

wheels:
	@echo "Creating distribution wheel"
	pipenv run python setup.py bdist_wheel

pypi-publish: build
	@echo "Publishing to Pypy"
	pipenv run python setup.py upload -r pypi

update:
	@echo "Updating dependencies..."
	pipenv update
	@echo "Consider updating 'bootstrap-system.sh' manually"

lock:
	pipenv lock
	pipenv install --dev

freeze:
	pipenv run pip freeze

clean:
	pipenv --rm ; true
	find . -name "*.pyc" -exec rm -f {} \;

githook:style readme

push: githook
	@git push origin --tags

# aliases to gracefully handle typos on poor dev's terminal
check: checks
devel: dev
develop: dev
dist: dists
docker-kill: kill-docker
docker-run: run-docker
docker: docker-build
build-docker: docker-build
image: docker
install: install-system
pypi: pypi-publish
run: run-local
styles: style
test: test-unit
upgrade: update
wheel: wheels
frontend-dev: dev-frontend
build-frontend: frontend-build
frontend-run: run-frontend
