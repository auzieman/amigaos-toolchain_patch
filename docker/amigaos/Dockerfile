ARG AMIGAOS_TOOLCHAIN_IMAGE
FROM ${AMIGAOS_TOOLCHAIN_IMAGE}
USER root
RUN case "$(/opt/ppc-amigaos/bin/ppc-amigaos-gcc -dumpversion)" in 6.*) ;; *) exit 1;; esac
COPY e500v2.specs /opt/tabor-spe/e500v2.specs
COPY compiler-wrapper /opt/tabor-spe/compiler-wrapper
RUN chmod 755 /opt/tabor-spe/compiler-wrapper && \
    mkdir /opt/tabor-spe/bin && \
    ln -s ../compiler-wrapper /opt/tabor-spe/bin/ppc-amigaos-gcc && \
    ln -s ../compiler-wrapper /opt/tabor-spe/bin/ppc-amigaos-g++
ENV PATH="/opt/tabor-spe/bin:${PATH}" \
    CC="/opt/tabor-spe/bin/ppc-amigaos-gcc" \
    CXX="/opt/tabor-spe/bin/ppc-amigaos-g++"
