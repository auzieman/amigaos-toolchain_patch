#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
static int matches(const char *pattern, const char *subject, int expected) {
    int error; PCRE2_SIZE offset;
    pcre2_code *code=pcre2_compile((PCRE2_SPTR)pattern,PCRE2_ZERO_TERMINATED,
                                 PCRE2_UTF|PCRE2_UCP,&error,&offset,NULL);
    if (!code) return 0;
    pcre2_match_data *data=pcre2_match_data_create_from_pattern(code,NULL);
    if (!data) { pcre2_code_free(code); return 0; }
    int rc=pcre2_match(code,(PCRE2_SPTR)subject,strlen(subject),0,0,data,NULL);
    pcre2_match_data_free(data); pcre2_code_free(code);
    return expected ? rc>0 : rc==PCRE2_ERROR_NOMATCH;
}
int main(void) {
    unsigned int jit=99;
    int configured=pcre2_config(PCRE2_CONFIG_JIT,&jit)==0 && jit==0;
    int ascii=matches("^A1222-[0-9]+$","A1222-42",1);
    int reject=matches("^A1222-[0-9]+$","A1222-SPE",0);
    int utf=matches("^\\p{L}+$","caf\xc3\xa9",1);
    int ok=configured && ascii && reject && utf;
    printf("PCRE2_SMOKE %s jit=%u ascii=%d reject=%d utf=%d\n",
           ok ? "PASS" : "FAIL",jit,ascii,reject,utf);
    return !ok;
}
