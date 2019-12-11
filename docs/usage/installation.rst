Installation
===============

	- Install MySQL

       - brew install mysql
	   - brew services start mysql

	- Install R:

       - brew install r

	- Install miniconda

       - brew cask install miniconda

	- Clone our repo

       - git clone https://github.com/JulioV/moshi-aware.git

	- Create a python virtual environment

       - conda env create -f environment.yml
       - conda init zsh/bash
       - Restart terminal if necessary
       - conda activate moshi-env

	- Install r packages:

       - snakemake packrat_install
       - snakemake packrat_init
       - snakemake packrat_restore

	- Configure the participants to analyze

       - Add a file per participant. Name it with the label for that participant (p01 for example): "/data/external/pxx" (no extension is necessary)
       - Add a line with the device_id for that participant as it appears on the db
       - Add a line with the mobile platform (Android, or iOS)

	- Configure the db connection

       - Create an empty .env file in the root folder
       - Add and complete the following lines
			[MY_GROUP_NAME]
			user=MyUSER
			password=MyPassword
			host=MyIP
			port=3306