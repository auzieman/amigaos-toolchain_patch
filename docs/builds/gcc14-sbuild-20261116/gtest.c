#include <stdio.h>
#include <string.h>
#include <glib.h>
#include <glib-object.h>
#include <gio/gio.h>

static guint sig;
static double got;

static void on_sig(GObject *o, double d, gint64 n, const char *s, gpointer u)
{
    (void)o; (void)u;
    got = d * 2 + (double)n + (double)strlen(s);
}

static gboolean quit(gpointer l) { g_main_loop_quit(l); return G_SOURCE_REMOVE; }

int main(void)
{
    GString *out = g_string_new(NULL);

    /* GVariant: print form, size, and a hash of the little-endian serialisation. */
    GVariant *n = g_variant_ref_sink(g_variant_new("(sidxa{sv}ay)", "spe", -42, 3.141592653589793,
                                                   G_GINT64_CONSTANT(-9000000000), NULL, NULL));
    GVariant *le = G_BYTE_ORDER == G_LITTLE_ENDIAN ? g_variant_ref(n) : g_variant_byteswap(n);
    GChecksum *ck = g_checksum_new(G_CHECKSUM_SHA256);
    g_checksum_update(ck, g_variant_get_data(le), g_variant_get_size(le));
    g_string_append_printf(out, "variant=%s size=%zu le-sha=%.16s\n", g_variant_print(n, TRUE),
                           g_variant_get_size(n), g_checksum_get_string(ck));

    char b1[G_ASCII_DTOSTR_BUF_SIZE], b2[G_ASCII_DTOSTR_BUF_SIZE];
    g_ascii_dtostr(b1, sizeof b1, 1.0 / 3.0);
    g_ascii_formatd(b2, sizeof b2, "%.10e", 6.02214076e23);
    g_string_append_printf(out, "dtostr=%s %s\n", b1, b2);
    g_string_append_printf(out, "strtod=%.17g\n", g_ascii_strtod("2.718281828459045e-3", NULL));

    GError *err = NULL;
    GRegex *re = g_regex_new("([a-z]+)@([a-z]+)[.]org", 0, 0, &err);
    GMatchInfo *mi = NULL;
    if (!re) {
        g_string_append_printf(out, "regex-error=%s\n", err->message);
    } else if (g_regex_match(re, "mail tabor@spe.org now", 0, &mi)) {
        g_string_append_printf(out, "regex=%s/%s\n", g_match_info_fetch(mi, 1), g_match_info_fetch(mi, 2));
    } else {
        g_string_append(out, "regex=nomatch\n");
    }

    GDateTime *dt = g_date_time_new_utc(2026, 11, 16, 5, 30, 15.25);
    g_string_append_printf(out, "date=%s unix=%" G_GINT64_FORMAT " dow=%d\n", g_date_time_format_iso8601(dt),
                           g_date_time_to_unix(dt), g_date_time_get_day_of_week(dt));
    g_string_append_printf(out, "utf8=%s len=%ld\n", g_utf8_strup("grüße ελλάδα", -1), g_utf8_strlen("grüße ελλάδα", -1));

    GHashTable *h = g_hash_table_new(g_str_hash, g_str_equal);
    for (int i = 0; i < 1000; i++)
        g_hash_table_insert(h, g_strdup_printf("k%d", i), GINT_TO_POINTER(i));
    g_string_append_printf(out, "hash=%u k777=%d\n", g_hash_table_size(h), GPOINTER_TO_INT(g_hash_table_lookup(h, "k777")));

    /* GObject signal with no C marshaller: g_cclosure_marshal_generic goes through libffi. */
    sig = g_signal_new("spe", G_TYPE_OBJECT, G_SIGNAL_RUN_LAST, 0, NULL, NULL, NULL, G_TYPE_NONE, 3,
                       G_TYPE_DOUBLE, G_TYPE_INT64, G_TYPE_STRING);
    GObject *o = g_object_new(G_TYPE_OBJECT, NULL);
    g_signal_connect(o, "spe", G_CALLBACK(on_sig), NULL);
    g_signal_emit(o, sig, 0, 1.25, G_GINT64_CONSTANT(5000000000), "abcd");
    g_string_append_printf(out, "signal=%.17g\n", got);

    GKeyFile *kf = g_key_file_new();
    g_key_file_load_from_data(kf, "[s]\nd=0.1\nl=1;2;3\n", -1, 0, NULL);
    gsize ln;
    gint *li = g_key_file_get_integer_list(kf, "s", "l", &ln, NULL);
    g_string_append_printf(out, "keyfile=%.17g %d%d%d\n", g_key_file_get_double(kf, "s", "d", NULL), li[0], li[1], li[2]);

    GMainLoop *l = g_main_loop_new(NULL, FALSE);
    g_timeout_add(20, quit, l);
    g_main_loop_run(l);
    g_string_append(out, "mainloop=ok\n");

    GFile *f = g_file_new_for_path("/tmp/gtest-spe.txt");
    g_file_replace_contents(f, "spe gio\n", 8, NULL, FALSE, 0, NULL, NULL, NULL);
    char *c; gsize cl;
    g_file_load_contents(f, NULL, &c, &cl, NULL, NULL);
    g_string_append_printf(out, "gio=%.*s", (int)cl, c);

    fputs(out->str, stdout);
    return 0;
}
