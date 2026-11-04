# Complete the existing Debian stage1 profile

The original stage1 profile omits libpam0g-dev and several PAM-related tools,
but leaves su/runuser on automatic detection. In the broad native dependency
template, native PAM headers allow detection even though target PAM libraries
are absent. SDK6 resolves the earlier header failure; normal compilation then
reaches missing -lpam/-lpam_misc while linking su.

0001 adds --disable-su/--disable-runuser only inside the existing stage1
branch. No ordinary-build option changes. This is a Debian bootstrap-profile
correction and must retain the subsequent full rebuild obligation. Original
source archives are unchanged; the runner prepares a separate reviewed DSC.

Round008 additionally selected pam_lastlog2 from native PAM headers. The
stage1-only correction includes --disable-pam-lastlog2, confirmed in the pinned
original configure.ac. No generic PAM module is omitted from full builds.

Three later consumers exposed a shared-file coinstallation failure: stage1
skips dh_installman, leaving uuid_generate_random.3 as a .so stub while native
uuid-dev contains expanded content. The main target page already matches the
native expanded alias exactly. The patch therefore retains normal
dh_installman --language=C in stage1. Native packaging regression verifies
byte-compatible output; complete rebuild/coinstallation acceptance is separate.
