# Item Catalog

> Chetanya Chopra

## About

This is a small catalog web application. Users can login via Google and create/modify new/exsisting items. This project was built using Python. 

## Used in this Project
- Python
- HTML
- CSS
- Bootstrap
- Flask
- SQLAchemy
- OAuth
- Google Login

## Required 
- [Vagrant](https://www.vagrantup.com/)
- [This repo](https://github.com/chetchop/Catalog-Project)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Getting Started

- Install Vagrant and VirtualBox
- Clone the Udacity vagrantfile
- Navigate to the vagrant folder and delete everything but the vagrant file
- While in this directory clone [This repo](https://github.com/chetchop/Catalog-Project)
- Now you should have a directory called `catalog=project` within your vagrant folder
- Navigate to the vagrant file within the vagrant folder via terminal/cmd/etc
- Run `vagrant up` to configure and run the virtual machine, 
- Run `vagrant ssh` to ssh into the VM
- To run the application, in the VM, navigate to /vagrant to access the shared files
- The navigate into the catalog-project folder where you will find the project and its dependencies
- Run application with `python project2.py`
- Go to `http://localhost:8000/catalog` in your browser to view the application

## JSON Endpoints

- Go to `http://localhost:8000/catalog.json`
- This will give you all of the categories and the items contained within them

## Know issues

- project2.py:27:1: E402 module level import not at top of file
- Running pycodestyle on the project2.py file gives the complaint above, but this is due to the need to import in modules from the database folder

