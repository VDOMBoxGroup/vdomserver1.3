#!/bin/sh
#
# $NetBSD: local,v 1.6 2002/03/22 04:33:59 thorpej Exp $
# $FreeBSD: src/etc/rc.d/local,v 1.6 2004/10/07 13:55:26 mtm Exp $
#

# PROVIDE: vdom
# REQUIRE: DAEMON
# BEFORE:  LOGIN
cd /vdom/bin

echo 'Starting debug...'
sleep 3
echo '...'
if [ -e /vdom/bin/debug ];
then
	/vdom/bin/debug
fi

