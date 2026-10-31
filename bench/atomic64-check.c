#include <stdint.h>
#include <stdio.h>
#include <pthread.h>
static uint64_t counter;
static void *worker(void *arg) { (void)arg; for(int i=0;i<10000;i++)__atomic_fetch_add(&counter,1,__ATOMIC_SEQ_CST);return NULL; }
int main(void) {
 pthread_t a,b;if(pthread_create(&a,NULL,worker,NULL)||pthread_create(&b,NULL,worker,NULL))return 1;
 pthread_join(a,NULL);pthread_join(b,NULL);
 uint64_t v=__atomic_load_n(&counter,__ATOMIC_SEQ_CST),expected=20000;
 if(v!=expected || !__atomic_compare_exchange_n(&counter,&expected,42,0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST) || __atomic_load_n(&counter,__ATOMIC_SEQ_CST)!=42)return 2;
 puts("ATOMIC64_TEST threaded_add_and_cas PASS");return 0;
}
