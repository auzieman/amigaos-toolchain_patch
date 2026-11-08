/*
 * Copyright 2015 Advanced Micro Devices, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER(S) OR AUTHOR(S) BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 */

typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef uint32_t ULONG;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define ATOM_BIG_ENDIAN 1
#define cpu_to_le32(x) __builtin_bswap32(x)
#else
#define ATOM_BIG_ENDIAN 0
#define cpu_to_le32(x) (x)
#endif
#define COMPUTE_GPUCLK_INPUT_FLAG_SCLK 1
static uint32_t get_unaligned_le32(const void *p) {
 const uint8_t *b=p; return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
}
static void put_unaligned_le32(uint32_t n,void *p) {
 uint8_t *b=p; b[0]=n;b[1]=n>>8;b[2]=n>>16;b[3]=n>>24;
}
typedef struct _COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4
{
#if ATOM_BIG_ENDIAN
  ULONG  ucPostDiv:8;        //return parameter: post divider which is used to program to register directly
  ULONG  ulClock:24;         //Input= target clock, output = actual clock
#else
  ULONG  ulClock:24;         //Input= target clock, output = actual clock
  ULONG  ucPostDiv:8;        //return parameter: post divider which is used to program to register directly
#endif
}COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4;
static void atomctrl_set_clock_word(void *word, uint32_t clock, uint8_t flags)
{
	put_unaligned_le32((clock & 0x00ffffff) | ((uint32_t)flags << 24), word);
}

static uint32_t atomctrl_clock_word_frequency(const void *word)
{
	return get_unaligned_le32(word) & 0x00ffffff;
}

static uint8_t atomctrl_clock_word_flags(const void *word)
{
	return get_unaligned_le32(word) >> 24;
}


int main(void);

void *memcpy(void *dst, const void *src, __SIZE_TYPE__ n) {
 volatile unsigned char *d=dst; const volatile unsigned char *s=src;
 for (__SIZE_TYPE__ i=0;i<n;i++) { d[i]=s[i]; }
 return dst;
}
static void emit(const char *p, unsigned n) {
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=4;
 register unsigned r3 __asm__("r3")=1;
 register const char *r4 __asm__("r4")=p;
 register unsigned r5 __asm__("r5")=n;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : "r"(r4),"r"(r5) : "cr0","memory");
#else
 long result;
 __asm__ volatile("syscall" : "=a"(result) : "0"(1L),"D"(1L),"S"(p),"d"((unsigned long)n) : "rcx","r11","memory");
#endif
}
static void hex(uint32_t n) {
 char b[9];const char *digits="0123456789abcdef";
 for(unsigned i=0;i<8;i++) b[i]=digits[(n >> (28-i*4))&15];
 b[8]=' ';emit(b,9);
}
void _start(void) {
 int r=main();
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=1;
 register unsigned r3 __asm__("r3")=r;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : : "cr0","memory");
#else
 __asm__ volatile("syscall" : : "a"(60L),"D"((long)r) : "rcx","r11","memory");
#endif
 __builtin_unreachable();
}

int main(void) {
 uint32_t clocks[]={30000,40000,50000,60000,70000,80000,90000,100000,0x123456,0xffffff};
 struct { COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4 ulClock; } pll_patameters;
 for (unsigned i=0;i<sizeof(clocks)/sizeof(clocks[0]);i++) {
  uint32_t clock_value=clocks[i];
  pll_patameters.ulClock.ulClock=0;
  pll_patameters.ulClock.ucPostDiv=0;
	atomctrl_set_clock_word(&pll_patameters.ulClock, clock_value,
				COMPUTE_GPUCLK_INPUT_FLAG_SCLK);

  hex(clock_value);hex(get_unaligned_le32(&pll_patameters.ulClock));emit("\n",1);
 }
 uint32_t output;
 atomctrl_set_clock_word(&output,0x123456,5);
 emit("out ",4);hex(atomctrl_clock_word_frequency(&output));hex(atomctrl_clock_word_flags(&output));emit("\n",1);
 return 0;
}
