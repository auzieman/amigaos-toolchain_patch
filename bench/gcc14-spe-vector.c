/* Separate translation unit so the caller cannot fold away the loop. */
void probe_array(float *restrict out, const float *restrict left,
                 const float *restrict right, unsigned count)
{
    for (unsigned i = 0; i < count; ++i)
        out[i] = left[i] + right[i];
}
