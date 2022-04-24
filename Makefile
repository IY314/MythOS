install:
	@printf "\e[34;1mMaking virtual environment...\e[m\n"
	@python -m venv venv
	@printf "\e[34;1mActivating shell environment...\e[m\n"
	@chmod u+x ./venv/bin/activate
	@./venv/bin/activate
	@printf "\e[34;1mInstalling packages...\e[m\n"
	@./venv/bin/pip install -U pip
	@./venv/bin/pip install -r requirements.txt

dev_pkgs: install
	@python -m pip install -r requirements_dev.txt; fi

cleanup:
	@rm -rf .mypy_cache venv
