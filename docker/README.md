# README 

To help lint & check the contents of this repo, docker resources have been
provided.

The simplest way to run the tests is to use `docker-compose`. Within the
docker directory, run `docker-compose run --rm <version>`, where version is
one of `2.7`,`3.4`,`3.5`,`3.6`. This will automatically build the docker 
images from the `docker_build` directory and run the `run_tests` script against
the `sensu_plugin` directory within the container, removing the container
one exit.

For any additional prerequisites that are needed (eg. python modules),
ammend `docker_build/setup.sh` and then run `docker_build/update` (This
copies the ammended `setup.sh` into each image directory). Procede to rebuild
the docker images, either via. 
`docker build -t python:2.7.14-sensuci ./docker_build/2.7`
or with `docker-compose build 2.7`.

If you are feeling adventurous, you can simply `docker-compose up` to build
and launch all of the containers at once!
