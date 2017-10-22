.PHONY: build

dev:
	npm install -g quasar-cli
	npm install

run:
	quasar dev

build:
	quasar build

version:
	npm version $(pbr info dopplerr | cut -f2)

release: version
