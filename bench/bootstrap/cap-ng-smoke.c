#include <cap-ng.h>
#include <stdio.h>
#include <unistd.h>
int main(void) {
    int get = capng_get_caps_process();
    int before = capng_have_capabilities(CAPNG_SELECT_BOTH);
    capng_clear(CAPNG_SELECT_BOTH); /* Local library state only, never capng_apply. */
    int empty = capng_have_capabilities(CAPNG_SELECT_BOTH);
    int reload = capng_get_caps_process();
    int after = capng_have_capabilities(CAPNG_SELECT_BOTH);
    int ok = get == 0 && reload == 0 && before >= 0
             && empty == CAPNG_NONE && after == before;
    printf("CAP_NG_SMOKE %s uid=%lu get=%d before=%d empty=%d reload=%d after=%d\n",
           ok ? "PASS" : "FAIL", (unsigned long)getuid(),get,before,empty,reload,after);
    return !ok;
}
