/* #8: do doubles and floats survive Eina's text conversion and Eet's encoding on this host?
 * Eet stores EET_T_DOUBLE/EET_T_FLOAT as eina_convert_dtoa/fptoa strings and reads them back with
 * eina_convert_atod/atofp, so a theme compiled on x86 is decoded on the A1222 through these.
 * For each value: eina_convert_dtoa string, eina_convert_atod + ldexp back, and an Eet data
 * descriptor round trip of a struct { double d; float f; }. Prints one line per value; any value
 * that does not come back identical is marked. Build natively and for the A1222 and diff. */
#include <Eina.h>
#include <Eet.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

typedef struct { double d; float f; } S;

int main(void)
{
   eina_init(); eet_init();
   Eet_Data_Descriptor_Class c;
   EET_EINA_STREAM_DATA_DESCRIPTOR_CLASS_SET(&c, S);
   Eet_Data_Descriptor *dd = eet_data_descriptor_stream_new(&c);
   EET_DATA_DESCRIPTOR_ADD_BASIC(dd, S, "d", d, EET_T_DOUBLE);
   EET_DATA_DESCRIPTOR_ADD_BASIC(dd, S, "f", f, EET_T_FLOAT);
   static const double v[] = { 0.0, -0.0, 1.0, -1.0, 0.5, 0.25, 0.1, 2.0, 3.0, 10.0, 0.75, 1.5,
                               255.0, 123.456, 1e-3, 1e-10, 65536.0, 4294967296.0, 9007199254740993.0,
                               0.333333333333, 1e300, 1e-300 };
   int bad = 0;
   for (unsigned i = 0; i < sizeof v / sizeof v[0]; i++) {
      char buf[128] = "";
      eina_convert_dtoa(v[i], buf);
      long long m = 0; long e = 0; double back = NAN;
      if (eina_convert_atod(buf, strlen(buf), &m, &e)) back = ldexp((double)m, e);
      S in = { v[i], (float)v[i] }, *out = NULL; int sz = 0;
      void *blob = eet_data_descriptor_encode(dd, &in, &sz);
      if (blob) out = eet_data_descriptor_decode(dd, blob, sz);
      int ok = back == v[i] && signbit(back) == signbit(v[i]) && out && out->d == in.d && out->f == in.f;
      bad += !ok;
      printf("%-22.17g dtoa=%-26s atod=%-22.17g m=%lld e=%ld eet d=%-22.17g f=%-14.9g %s\n", v[i], buf, back, m, e,
             out ? out->d : NAN, out ? (double)out->f : NAN, ok ? "ok" : "MISMATCH");
   }
   printf("RESULT %s (%d)\n", bad ? "FAIL" : "PASS", bad);
   return bad != 0;
}
