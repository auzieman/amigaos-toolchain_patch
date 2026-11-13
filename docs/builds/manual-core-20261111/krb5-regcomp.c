#include <sys/types.h>
#include <regex.h>
#include <gnu/libc-version.h>
#include <stdio.h>
int main(void){regex_t x;regmatch_t m;int r=regcomp(&x,"pat.*",0);if(!r){r=regexec(&x,"pattern",1,&m,0);regfree(&x);}printf("libc=%s result=%d\n",gnu_get_libc_version(),r);return r;}
