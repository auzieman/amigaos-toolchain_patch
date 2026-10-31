/* Match libXext configure's XORG_CHECK_MALLOC_ZERO predicate exactly. */
#include <stdio.h>
#include <stdlib.h>
int main(void) {
 void *m=malloc(0), *p=malloc(10);if(!p)return 2;
 void *r=realloc(p,0), *c=calloc(0,10);
 int result=(m==NULL || r==NULL || c==NULL);
 printf("XORG_ALLOC_ZERO malloc_null=%d realloc_null=%d calloc_null=%d xorg_cv_malloc0_returns_null=%s\n",m==NULL,r==NULL,c==NULL,result?"yes":"no");
 free(m);free(r);free(c);return 0;
}
