# Ovule-auto-pipeline
Plant developmental biology: Automation pipeline for the data analysis of ovules

How to get started through the virtual machine:
1.	Open a terminal on your notebook.
2.	Log into the virtual machine by i) running “ssh username@ip-address”, where username and IP-address must be replaced accordingly, and ii) entering the password for the chosen user. Now you should be logged in.
3.	Now, the base environment is activated. However, we want to activate the environment 3d-ovule-ana-env, in which all necessary Python libraries are already installed. Activate the conda environment 3d-ovule-ana-env by running “conda activate 3d-ovule-ana-env”. If successful, (3d-ovule-ana-env) instead of (base) will appear to the left of the username.
4.	Now, run “jupyter notebook”. Copy the URL starting with http://..., replace "tuwzu6a-plantdevpostgres" with the IP-address and open it in the browser of your choice.
5.	You will now see all files stored in the virtual machine (in the directory you are currently located, i.e., /home/ovule). Open the folder 3D-ovule-analysis-pipeline by clicking on it.
6.  Open the notebook getting_started.ipynb. This notebook guides you through the basics, i.e., how to connect to the database and load data tables from it, how to perform basic statistical analyses and visualize the results, etc. Use it as a guide for future analyses that you might want to perform.
