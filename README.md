# pdf_gen_poc


## Quickstart

This component comes with a Docker configuration to setup a development environment in no time.

### Prerequisites

* [Docker](https://docs.docker.com/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* No other services listening on TCP ports **9000** , be aware for redis ports that might overlap if you have other running components.

### Step by step

#### 1. Clone this repository:

```bash
git clone git@github.com:vikingco/pdf_gen_poc.git
```

#### 2. Step into the directory

```bash
cd pdf_gen_poc/
```

#### 3. Copy your personal ssh key

Copy a personal private SSH key - with rights to access the Unleashed repos on GitHub - 
into deployment/.ssh/ with the name of "id_rsa" (feel free to create a new one for this specific reason).
You cannot symlink because docker will not follow those. (You could always double check now that ".ssh" 
is still present in the ".gitignore" file, because this information should not be checked in and pushed 
to GitHub.

Make sure it's a passwordless key. If Git needs a password to unlock your SSH key during the build, 
the build automation unfortunately breaks. You could mitigate this security risk by encrypting 
your hard drive.


It might be a good idea to tweak the rights to this ".ssh" directory, e.g. in the ".ssh" directory 
execute the following command:
```bash
chmod 600 .ssh/id_rsa
```

#### 4. Build the docker environment. (It will prepare your runtime and dev environment.)

To build the container, just run:
```bash
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```
You can also set the `COMPOSE_DOCKER_CLI_BUILD` and `DOCKER_BUILDKIT` variables in your environment for conveniences.

#### 5. Run the docker environment

```bash
docker-compose up
```

#### 6. Shut down the container

```bash
CTRL-C
```

#### 7. Create the database

```bash
docker-compose run --rm pdf-gen-poc python manage.py migrate
```

#### 8. Run the docker environment

```bash
docker-compose up
```

#### 10. Verify everything's working

Open your browser and go to [http://0.0.0.0:9000/admin](http://0.0.0.0:9000/admin).
If all went well, you should see a login screen into the admin.

### 11. Set up git config

Install `pre-commit` as in the `requirements_test.txt` (either in a virtualenv or with something like `brew`), and
install the hooks by running

```bash
pre-commit install
```
