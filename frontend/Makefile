.PHONY: build

dev:
	npm install -g npm@latest quasar-cli
	npm install

run:
	quasar dev

build:
	quasar build

version:
	npm version $(pbr info dopplerr | cut -f2)

release: version

clean:
	rm -rf node_modules/
