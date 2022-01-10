.PHONY: clean pre-commit


pre-commit:
	pip3 install git-pylint-commit-hook
	# Copy script for git pre-commit
	cp scripts/pre-commit .git/hooks/

clean:
	rm .git/hooks/pre-commit


help:
	@echo "    clean"
	@echo "        Delete pre-commit script"
	@echo '    pre-commit'
	@echo '        Register pre-commit hook script.'