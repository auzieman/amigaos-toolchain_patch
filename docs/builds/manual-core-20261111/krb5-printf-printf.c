#include <stdio.h>
#include <string.h>
#include <gnu/libc-version.h>
int main(void){char buf[30];sprintf(buf,"%2$x %1$d",100,512);printf("libc=%s actual=<%s> expected=<200 100>\n",gnu_get_libc_version(),buf);return strcmp("200 100",buf)!=0;}
