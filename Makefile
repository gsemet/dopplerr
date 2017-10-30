.PHONY: build

MODULE:=dopplerr
DOCKER_BUILD?=docker build
PORT:=8086
LANGUAGES?=fra,eng
BASEDIR?=dopplerr/tests/vectors/basedir
MAPPING?=tv=Series
OPENSUBTITLES_USERNAME?=username
OPENSUBTITLES_PASSWORD?=password
PUSHOVER_USER?=user
PUSHOVER_TOKEN?=token

all: frontend-all backend-all
backend-all: dev version style checks frontend-build build dists docker-build test-unit
frontend-all: frontend-dev frontend-build
all-local: dev style checks dists test-unit
all-docker: dev style checks docker-build test-unit

all-dev: frontend-dev backend-dev
release: requirements version readme frontend-build backend-build

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
	pipenv install --system --skip-lock

style: readme requirements isort autopep8 yapf

isort:
	pipenv run isort -y

autopep8:
	pipenv run autopep8 --in-place --recursive setup.py $(MODULE)

yapf:
	pipenv run yapf --style .yapf --recursive -i $(MODULE)

checks: readme requirements flake8 pylint

sc: readme requirements style checks

flake8:
	pipenv run python setup.py flake8

pylint:
	pipenv run pylint --rcfile=.pylintrc --output-format=colorized $(MODULE)

requirements:
	pipenv run pipenv_to_requirements

build: readme requirements version dists

readme:
    # Only for Pypi, which does not render MarkDown Readme
	pandoc --from=markdown --to=rst --output=README.rst README.md

run-local:
	@echo "Starting Dopplerr on http://localhost:$(PORT) ..."
	pipenv run $(MODULE) \
	           -p $(PORT) \
	           -v \
	           -l "debug.log" \
	           -m $(MAPPING) \
	           -b $(BASEDIR) \
	           --subliminal-languages $(LANGUAGES) \
	           --subliminal-opensubtitles-enabled \
	           --subliminal-opensubtitles-user $(OPENSUBTITLES_USERNAME) \
	           --subliminal-opensubtitles-password $(OPENSUBTITLES_PASSWORD) \
	           --notifications-pushover-enabled \
	           --notifications-pushover-user $(PUSHOVER_USER) \
	           --notifications-pushover-token $(PUSHOVER_TOKEN) \

postman-sonarr:
	pipenv run curl -X POST \
	                -H "Content-Type: application/json" \
	                -H "Accept: application/json" \
	                --data "@dopplerr/tests/vectors/sonarr_on_download2.json" \
	                http://localhost:$(PORT)/api/v1/notify/sonarr

postman: postman-sonarr

run-local-env:
	@echo "Starting Dopplerr on http://localhost:$(PORT) using environment variable parameters..."
	DOPPLERR_GENERAL_PORT=$(PORT) \
	    DOPPLERR_GENERAL_MAPPING="$(MAPPING)" \
	    DOPPLERR_GENERAL_BASEDIR=$(BASEDIR) \
	    DOPPLERR_SUBLIMINAL_LANGUAGES=$(LANGUAGES) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_ENABLED=$(OPENSUBTITLES_USERNAME) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_USER=$(OPENSUBTITLES_USERNAME) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_PASSWORD=$(OPENSUBTITLES_PASSWORD) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_ENABLED=$(PUSHOVER_USER) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_USER=$(PUSHOVER_USER) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_TOKEN=$(PUSHOVER_TOKEN) \
	    pipenv run $(MODULE) \
	        --verbose \
	        --logfile "debug.log"

run-docker: kill-docker
	docker run -p $(PORT):$(PORT) \
	           -e "DOPPLERR_GENERAL_MAPPING='$(MAPPING)'" \
	           -e "DOPPLERR_GENERAL_LOGFILE=debug.log" \
	           -e "DOPPLERR_GENERAL_BASEDIR=$(BASEDIR)" \
	           -e "DOPPLERR_SUBLIMINAL_LANGUAGES=$(LANGUAGES)" \
	           -e "DOPPLERR_SUBLIMINAL_OPENSUBTITLES_ENABLED=1" \
	           -e "DOPPLERR_SUBLIMINAL_OPENSUBTITLES_USER=$(OPENSUBTITLES_USERNAME)" \
	           -e "DOPPLERR_SUBLIMINAL_OPENSUBTITLES_PASSWORD=$(OPENSUBTITLES_PASSWORD)" \
	           -e "DOPPLERR_NOTIFICATIONS_PUSHOVER_ENABLED=1" \
	           -e "DOPPLERR_NOTIFICATIONS_PUSHOVER_USER=$(PUSHOVER_USER)" \
	           -e "DOPPLERR_NOTIFICATIONS_PUSHOVER_TOKEN=$(PUSHOVER_TOKEN)" \
	           -t dopplerr:latest

run_frontend:
	cd frontend ; make run

kill-docker:
	docker kill $$(docker ps --format '{{.Names}}\t{{.Image}}\t' | grep dopplerr | cut -f1) || true

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
	rm -rf cachefile.dbm*
	rm -f *.log
	rm -rf .eggs *.egg-info

frontend-clean:
	cd frontend ; make clean

githook:style readme version

push: githook
	git push origin --all
	git push origin --tags

# aliases to gracefully handle typos on poor dev's terminal
check: checks
backend-checks: checks
backend-build: build
backend-clean: clean
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
unittest: test-unit
unittests: test-unit
upgrade: update
wheel: wheels
dev-frontend: frontend-dev
build-frontend: frontend-build
frontend-run: run-frontend
build-backend: build
dev-backend: dev
backend-dev: dev
