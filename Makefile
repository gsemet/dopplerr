.PHONY: build

CMD:=dopplerr
MODULES:=dopplerr cfgtree
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

dev: pipenv-install-dev ln-venv

pipenv-install-dev:
	@echo "Setting up development environment"
	pipenv install --dev

pipenv-install-system-dev:
	@echo "Setting up development environment"
	pipenv install --dev --system

ln-venv:
	@# this target creates a .venv link to your virtual env binaries
	@# useful for some editors that does not know how to find the venv automatically
	@ln -sf $$(pipenv --venv) .venv

frontend-dev:
	cd frontend ; make dev

frontend-build:
	cd frontend ; make build

frontend-run:
	cd frontend ; make run

frontend-lint:
	cd frontend ; make lint

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
	pipenv run autopep8 --in-place --recursive setup.py $(MODULES)

yapf:
	pipenv run yapf --style .yapf --recursive -i $(MODULES)

checks: readme requirements flake8 pylint

sc: readme requirements style checks

flake8:
	pipenv run python setup.py flake8

pylint:
	pipenv run pylint --rcfile=.pylintrc --output-format=colorized $(MODULES)

requirements:
	pipenv run pipenv_to_requirements

build: readme requirements version dists

readme:
    # Only for Pypi, which does not render MarkDown Readme
	pandoc --from=markdown --to=rst --output=README.rst README.md

run-local:
	@echo "Starting dev-log Dopplerr on http://localhost:$(PORT) ..."
	PYTHONASYNCIODEBUG=1 \
	    pipenv run $(CMD) \
	           --output-type dev \
	           --debug-config \
	           --verbose \
	           -l "debug.log" \
	           -p $(PORT) \
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
	@echo "Starting plain log Dopplerr on http://localhost:$(PORT) "
	@echo "using environment variable parameters..."
	DOPPLERR_GENERAL_PORT=$(PORT) \
	    DOPPLERR_VERBOSE=1 \
	    DOPPLERR_GENERAL_MAPPING="$(MAPPING)" \
	    DOPPLERR_GENERAL_BASEDIR=$(BASEDIR) \
	    DOPPLERR_SUBLIMINAL_LANGUAGES=$(LANGUAGES) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_ENABLED=$(OPENSUBTITLES_USERNAME) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_USER=$(OPENSUBTITLES_USERNAME) \
	    DOPPLERR_SUBLIMINAL_OPENSUBTITLES_PASSWORD=$(OPENSUBTITLES_PASSWORD) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_ENABLED=$(PUSHOVER_USER) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_USER=$(PUSHOVER_USER) \
	    DOPPLERR_NOTIFICATIONS_PUSHOVER_TOKEN=$(PUSHOVER_TOKEN) \
	    pipenv run $(CMD) \
	        --output-type plain

run-docker: kill-docker
	@echo "Starting plain-log Dopplerr on http://localhost:$(PORT) "
	docker run -p $(PORT):$(PORT) \
	           -e "DOPPLERR_VERBOSE=1" \
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
	PYTHONASYNCIODEBUG=1 \
		pipenv run pytest  --junitxml=junit.xml -v $(MODULES)

test-unit-v:
	PYTHONASYNCIODEBUG=1 \
		pipenv run pytest  --junitxml=junit.xml -v -s $(MODULES)

test-v: test-unit-v

docker-build:
	@echo "Testing docker build"
	@echo "You can change the default 'docker build' command line with the DOCKER_BUILD environment variable"
	$(DOCKER_BUILD) -t $(CMD) .

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
	pipenv install --dev
	@echo "Consider updating 'bootstrap-system.sh' manually"

lock:
	pipenv lock
	pipenv install --dev

freeze:
	pipenv run pip freeze

clean:
	pipenv --rm ; true
	find . -name '__pycache__' -delete
	find . -name "*.pyc" -exec rm -f {} \;
	rm -rf cachefile.dbm*
	rm -f *.log
	rm -f *.log.*
	rm -rf .eggs *.egg-info
	rm -rf _trial_temp/
	rm -rf dist/ build/
	rm -rf .venv
	# note: keep sqlite.db

clean-db:
	rm -f sqlite.db

frontend-clean:
	cd frontend ; make clean

clean-all: frontend-clean clean clean-db

githook:style readme version

push: githook
	git push origin --all
	git push origin --tags

# aliases to gracefully handle typos on poor dev's terminal
backend-build: build
backend-checks: checks
backend-clean: clean
backend-dev: dev
build-backend: build
build-docker: docker-build
build-frontend: frontend-build
check: checks
dev-backend: dev
dev-frontend: frontend-dev
devel: dev
develop: dev
dist: dists
docker-kill: kill-docker
docker-run: run-docker
docker: docker-build
frontend-run: run-frontend
frontend: frontend-all
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
