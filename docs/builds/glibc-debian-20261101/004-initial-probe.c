#define _GNU_SOURCE
#include <link.h>
#include <stdio.h>
#include <unistd.h>
__attribute__((noinline)) static void *caller(void) {
    char buf[32];
    buf[0] = (char)getpid();
    asm volatile("" : : "m"(buf) : "memory");
    return __builtin_extract_return_addr(__builtin_return_address(0));
}
static int count;
static int visit(struct dl_phdr_info *info, size_t size, void *data) {
    (void)info; (void)size; (void)data; ++count; return 0;
}
int main(void) {
    void *p = caller();
    printf("RETURN_ADDRESS %p main=%p\n",p,(void *)main); fflush(stdout);
    int ret = dl_iterate_phdr(visit,0);
    printf("PHDR_COUNT %d result=%d\n",count,ret);
    return count < 2;
}
