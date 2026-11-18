#!/bin/sh
# #8: assemble a chroot for the A1222 from the efl-001 stage, without auzieman's rescue initramfs.
# Same filtering as stage-e-root.py (no headers, docs, man, pkg-config, static archives, build
# work or E's backgrounds); ELFs are kept unstripped. Runtime glibc comes from the SDK sysroot the
# stage was linked against, libgcc_s/libstdc++/libatomic from the SDK, DejaVu 2.37-8 (the lock's
# version) from the replica host. Busybox and the mounts are added on the board. Output: e8-root.tar
set -e
W=/srv/data1/tabor-build/work/e8; S=$W/runs/efl-001/stage; R=$W/chroot
T=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
rm -rf $R; mkdir -p $R/lib $R/usr/lib $R/bin $R/dev $R/proc $R/sys $R/run $R/home/tabor $R/tmp/.X11-unix $R/usr/share/fonts/truetype
tar -C $S -cf - --exclude=usr/include --exclude=usr/share/doc --exclude=usr/share/man --exclude=usr/share/info \
  --exclude=usr/share/aclocal --exclude=usr/share/pkgconfig --exclude=usr/lib/pkgconfig --exclude=usr/lib/cmake \
  --exclude='*.a' --exclude='*.la' --exclude='*.h' --exclude=usr/share/enlightenment/data/backgrounds etc usr var | tar -C $R -xf -
cp -a $T/sysroot/lib/*.so* $T/sysroot/lib/ld.so.1 $R/lib/
cp -a $T/powerpc-linux-gnuspe/lib/libgcc_s.so* $T/powerpc-linux-gnuspe/lib/libstdc++.so.6* $T/powerpc-linux-gnuspe/lib/libatomic.so* $R/usr/lib/
rm -f $R/usr/lib/libstdc++.so.6.*-gdb.py
cp -a /usr/share/fonts/truetype/dejavu $R/usr/share/fonts/truetype/
chmod 1777 $R/tmp $R/tmp/.X11-unix
printf 'root:x:0:0:root:/root:/bin/sh\ntabor:x:1000:1000:tabor:/home/tabor:/bin/sh\nmessagebus:x:100:101::/run:/bin/false\n' > $R/etc/passwd
printf 'root:x:0:\ntabor:x:1000:\nmessagebus:x:101:\n' > $R/etc/group
printf 'passwd: files\ngroup: files\nhosts: files\n' > $R/etc/nsswitch.conf
chown -R 1000:1000 $R/home/tabor
cp $W/x8-redirect $R/usr/bin/
tar -C $R -cf $W/e8-root.tar . && du -sh $R $W/e8-root.tar && sha256sum $W/e8-root.tar
