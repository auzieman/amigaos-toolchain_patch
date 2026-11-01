#include <sepol/policydb.h>
#include <stdio.h>
int main(void) {
    sepol_policydb_t *db = NULL;
    int rc = sepol_policydb_create(&db);
    int ok = rc == 0 && db != NULL;
    if (db) sepol_policydb_free(db);
    printf("SEPOL_SMOKE %s create=%d\n", ok ? "PASS" : "FAIL", rc);
    return !ok;
}
