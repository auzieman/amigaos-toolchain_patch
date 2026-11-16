#!/bin/bash
# Replica-local: print "<binNMU number> <timestamp>" for an amd64 binary package in the frozen snapshot ("0" if not a binNMU).
docker run --rm tabor-local/frozen-root-001 bash -c "apt-get update -qq >/dev/null 2>&1; v=\$(apt-cache show $1 2>/dev/null | sed -n 's/^Version: //p' | head -1); case \"\$v\" in *+b[0-9]*) n=\${v##*+b}; cd /tmp; apt-get download -qq $1:amd64 2>/dev/null; dpkg-deb -x ${1}_*amd64.deb x; c=\$(ls x/usr/share/doc/*/changelog.Debian.amd64.gz | head -1); echo \"\$n \$(zcat \$c | grep -m1 '^ -- ' | sed 's/.*>  //')\";; '') echo 'missing';; *) echo 0;; esac"
