#!/bin/bash

java -Dcom.sun.jndi.ldap.object.trustURLCodebase=true \
     -Dcom.sun.jndi.rmi.object.trustURLCodebase=true \
     -Dlog4j2.formatMsgNoLookups=false \
     -jar target/ctf-0.0.1-SNAPSHOT.jar 