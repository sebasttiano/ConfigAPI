.PHONY: clean dependency prepare pre-commit all

dependency:
ifneq (,$(wildcard /usr/bin/docker-compose))
	@echo "Docker-compose is installed in a system"
else
	sudo apt update -qy && sudo apt install docker-compose -y
endif

prepare:
	sudo mkdir /var/log/confapi

pre-commit:
	pip3 install git-pylint-commit-hook
	# Copy script for git pre-commit
	cp scripts/pre-commit .git/hooks/

build: dependency prepare
	docker-compose build

run: build
	docker-compose up -d

clean:
	docker-compose down
	rm .git/hooks/pre-commit
#    pip3 uninstall git-pylint-commit-hook

all: pre-commit run

help:
	@echo "    clean"
	@echo "        Stop all containers. And delete pre-commit script"
	@echo '    pre-commit'
	@echo '        Register pre-commit hook script.'
	@echo '    run'
	@echo '        Run all containers'
	@echo '    all'
	@echo '        Enable pre-commit, build and run all containers '