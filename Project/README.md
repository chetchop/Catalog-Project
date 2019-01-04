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
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Getting Started

- Install Vagrant and VirtualBox
- Clone [This repo](https://github.com/chetchop/Catalog-Project)
- Now you should have a directory called `catalog-project`. Inside you should have a vagrant file and a project folder
- Navigate to the vagrant file via terminal/cmd/etc
- Run `vagrant up` to configure and run the virtual machine, 
- Run `vagrant ssh` to ssh into the VM
- To run the application, in the VM, navigate to vagrant using `cd /vagrant`
- Then cd into the project folder
- Here you will find the project and its dependencies
- Run application with `python project2.py`
- Go to `http://localhost:8000/catalog` in your browser to view the application

## JSON Endpoints

- Go to `http://localhost:8000/catalog.json`
- This will give you all of the categories and the items contained within them
- Note that you need to be logged in to view it


