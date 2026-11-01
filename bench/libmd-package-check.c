/* Runtime check for the library extracted from the newly built Debian package. */
#include <md5.h>
#include <sha256.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    char md5[33], sha256[65];
    if (!MD5Data((const unsigned char *)"abc", 3, md5) ||
        !SHA256Data((const unsigned char *)"abc", 3, sha256)) return 1;
    if (strcmp(md5, "900150983cd24fb0d6963f7d28e17f72") ||
        strcmp(sha256, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")) return 1;
    puts("LIBMD_PACKAGE_CHECK PASS md5+sha256 known vectors");
    return 0;
}
