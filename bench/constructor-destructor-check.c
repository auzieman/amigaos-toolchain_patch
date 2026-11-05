/* Separate target-runtime validation for Kerberos's Autoconf cache predicate. */
#include <unistd.h>
static void before_main(void) __attribute__((constructor));
static void after_main(void) __attribute__((destructor));
static void before_main(void) { unlink("constructor.pending"); }
static void after_main(void) { unlink("destructor.pending"); }
int main(void) { return access("constructor.pending", F_OK) == 0; }
