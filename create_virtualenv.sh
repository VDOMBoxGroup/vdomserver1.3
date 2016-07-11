#!/bin/bash

XAPIAN_VERSION="1.2.23";

VENV="$1";

# create virtualenv is not exists
if [ ! -d "$VENV" ]; then
	virtualenv "$VENV";
fi


VENV=$(cd "$1"; pwd);

# install pip requirements
$VENV/bin/pip install -r requirements.txt;



# install xapian
mkdir -p $VENV/packages && cd $VENV/packages;

wget http://oligarchy.co.uk/xapian/1.2.23/xapian-core-${XAPIAN_VERSION}.tar.xz;
wget http://oligarchy.co.uk/xapian/1.2.23/xapian-bindings-${XAPIAN_VERSION}.tar.xz;

tar xf xapian-core-${XAPIAN_VERSION}.tar.xz;
tar xf xapian-bindings-${XAPIAN_VERSION}.tar.xz;

cd $VENV/packages/xapian-core-${XAPIAN_VERSION};
./configure --prefix=$VENV && make && make install;

export LD_LIBRARY_PATH=$VENV/lib;
PATH=$VENV/bin:$PATH;

cd $VENV/packages/xapian-bindings-${XAPIAN_VERSION};
./configure --prefix=$VENV --with-python && make && make install;

$VENV/bin/python -c "import xapian" && echo -e "\n\nComplete.\n\n";
