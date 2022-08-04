#!/bin/bash
docker pull mysql
docker run -p 3307:3306 --name mysql_container -e MYSQL_ROOT_PASSWORD=healthcare -e MYSQL_DATABASE=healthcare -v healthcare-db:/var/lib/mysql --restart always -d mysql
