VDOM Server v1.3
================

## Installation

The first you need to prepare environment with VDOM Server requirements. There are the list of requirements in `requirements.txt` file and `create_virtualenv.sh` is the bash script for easy creating of virtual python environment and installing requirements there.

```sh
    $ ./create_virtualenv.sh <DIR_NAME>
```

For example, create virtual environment in "venv" directory:

```sh
	$ ./create_virtualenv.sh "venv"
```

If you need environment with special dependencies, you can create it in separate steps. For example, create environment with Python 2.7.10:

```sh
	$ virtualenv --python=/usr/local/lib/python2.7.10/bin/python "venv2.7.10"
	$ ./create_virtualenv.sh "venv2.7.10" # script only install requirements
```

## Configuration

Configuration options contains in `bin/vdom.cfg` file. For example, for change server port to `8080`, set 
```
    SERVER-PORT = 8080
```

## Starting VDOM Server

You must to use created python environment to launch VDOM Server. Startup script is `bin/vdomsvr.py`

```sh
    $ cd bin/
	$ ../venv/bin/python vdomsvr.py -c vdom.cfg
```

After VDOM Server has loaded, check in browser admin page: `http://localhost:8080/system`
Default credentials is: `root:root`
