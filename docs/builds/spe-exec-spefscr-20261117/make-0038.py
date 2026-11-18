#!/usr/bin/env python3
"""Edit arch/powerpc/kernel/process.c for #48: exec starts with a defined SPEFSCR.

Usage: make-0038.py <path to process.c>   (edits in place; fails if the anchor is missing)
"""
import sys

path = sys.argv[1]
src = open(path).read()
old = """#ifdef CONFIG_SPE
	memset(current->thread.evr, 0, sizeof(current->thread.evr));
	current->thread.acc = 0;
	current->thread.spefscr = 0;
	current->thread.used_spe = 0;
#endif /* CONFIG_SPE */
"""
new = """#ifdef CONFIG_SPE
	memset(current->thread.evr, 0, sizeof(current->thread.evr));
	current->thread.acc = 0;
	/*
	 * Start the new image with the exception enables INIT_THREAD has
	 * (SPEFSCR_INIT) and glibc's FE_DFL_ENV sets: the IEEE fix-ups for
	 * Inf, NaN and denormal operands trap through them. Write the
	 * register as well as the saved copy. save_sprs() stores the
	 * hardware SPEFSCR at the first switch-out, so with only the saved
	 * copy set the image ran with its exec caller's SPEFSCR; and
	 * flush_all_to_thread() reads the hardware only when MSR_SPE is set,
	 * so a child forked before the image used SPE inherited the saved 0
	 * and ran with every enable clear.
	 */
	preempt_disable();
	{
		const unsigned long spefscr = SPEFSCR_FINVE | SPEFSCR_FDBZE |
					      SPEFSCR_FUNFE | SPEFSCR_FOVFE;

		current->thread.spefscr = spefscr;
		current->thread.spefscr_last = spefscr;
		if (cpu_has_feature(CPU_FTR_SPE))
			mtspr(SPRN_SPEFSCR, spefscr);
	}
	preempt_enable();
	current->thread.used_spe = 0;
#endif /* CONFIG_SPE */
"""
if src.count(old) != 1:
    sys.exit("anchor not found exactly once: start_thread CONFIG_SPE block")
open(path, "w").write(src.replace(old, new))
