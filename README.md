# SSTI-Research-and-Analysis
Research and Analysis about Server-Side Template Injection in DIMI class

<br>

## Getting started
_Version Info: python(3.9.8), Docker(20.10.10), docker-compose(1.29.2)_
1. Download ZIP or clone this github repository
2. Run `docker-compose up -d --build` command on the path where the ***docker-compose.yml*** file is located
3. When you want to stop, run the `docker-compose down` command in the path

<br>

## Changing the port
Open the `docker-compose.yml` file and replace it on services > nginx > ports > "{new_port}:5000" 
```yml
version: "3.3"

services:
    flask:
        build: ./flask
        container_name: flask
        restart: always
        environment:
            - APP_NAME=FlaskTest
        expose:
            - 8080

    nginx:
        build: ./nginx
        container_name: nginx
        restart: always
        ports:
            - "40000:5000"      # Change 40000 to new port
```
default port number is 40000
