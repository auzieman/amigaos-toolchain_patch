Use $tabor-debian-port. Continue the frozen Trixie powerpcspe port on the R730.
Provision the full selected sources' native build dependencies and package
cache before compiling. Extend source intake to the missing target dependency
producers using Debian metadata, keeping the selected baseline fixed. Run up
to four independent dependency-ready sbuild jobs; retain failures and continue
other ready work. Resolve shared infrastructure and dependency closure before
making individual source patches. Preserve Debian package installation and
configuration behavior. Report actual worker activity and the remaining gate
to an apt-installed X11/E workstation, then validate the new image in QEMU.
