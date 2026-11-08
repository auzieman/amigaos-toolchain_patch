
#include <stdio.h>
typedef int PPSMC_Msg;
struct pp_hwmgr {int chip_id; struct {int platformCaps;} platform_descriptor;};
static int fail_table,fail_dpm,late_calls;
#define CHIP_VEGAM 10
#define CHIP_POLARIS10 5
#define PHM_PlatformCaps_EngineSpreadSpectrumSupport 1
#define PHM_PlatformCaps_ThermalController 2
#define phm_cap_enabled(a,b) 0
#define PHM_WRITE_INDIRECT_FIELD(...) ((void)0)
#define PP_INIT_CALL(h,c) (c)
#define PP_ASSERT_WITH_CODE(c,m,a) do { if (!(c)) { a; } } while(0)
static int smu7_voltage_control(struct pp_hwmgr *h) {return 0;}
static int smum_initialize_mc_reg_table(struct pp_hwmgr *h) {return 0;}
static int smum_send_msg_to_smc(struct pp_hwmgr *h,int m,void*p){return 0;}
#define PPSMC_NoDisplay 0
static void smu7_populate_umdpstate_clocks(struct pp_hwmgr*h){}
static int smu7_construct_voltage_tables(struct pp_hwmgr*h){return 0;}
static int smu7_enable_deep_sleep_master_switch(struct pp_hwmgr*h){return 0;}
static int smu7_enable_didt_config(struct pp_hwmgr*h){return 0;}
static int smu7_enable_display_gap(struct pp_hwmgr*h){return 0;}
static int smu7_enable_power_containment(struct pp_hwmgr*h){return 0;}
static int smu7_enable_sclk_control(struct pp_hwmgr*h){return 0;}
static int smu7_enable_smc_cac(struct pp_hwmgr*h){late_calls++; return 0;}
static int smu7_enable_smc_voltage_controller(struct pp_hwmgr*h){return 0;}
static int smu7_enable_thermal_auto_throttle(struct pp_hwmgr*h){return 0;}
static int smu7_enable_ulv(struct pp_hwmgr*h){return 0;}
static int smu7_enable_voltage_control(struct pp_hwmgr*h){return 0;}
static int smu7_enable_vrhot_gpio_interrupt(struct pp_hwmgr*h){return 0;}
static int smu7_initial_switch_from_arbf0_to_f1(struct pp_hwmgr*h){return 0;}
static int smu7_notify_has_display(struct pp_hwmgr*h){return 0;}
static int smu7_pcie_performance_request(struct pp_hwmgr*h){return 0;}
static int smu7_populate_edc_leakage_registers(struct pp_hwmgr*h){return 0;}
static int smu7_power_control_set_level(struct pp_hwmgr*h){return 0;}
static int smu7_program_static_screen_threshold_parameters(struct pp_hwmgr*h){return 0;}
static int smu7_program_voting_clients(struct pp_hwmgr*h){return 0;}
static int smu7_setup_default_dpm_tables(struct pp_hwmgr*h){return 0;}
static int smu7_start_dpm(struct pp_hwmgr*h){return fail_dpm ? -22 : 0;}
static int smum_init_smc_table(struct pp_hwmgr*h){return fail_table ? -5 : 0;}
static int smum_process_firmware_header(struct pp_hwmgr*h){return 0;}
static int baseline_run(struct pp_hwmgr *hwmgr)
{
	int tmp_result = 0;
	int result = 0;

	if (smu7_voltage_control(hwmgr)) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_voltage_control(hwmgr));
		PP_ASSERT_WITH_CODE(tmp_result == 0,
				"Failed to enable voltage control!",
				result = tmp_result);

		tmp_result = PP_INIT_CALL(hwmgr, smu7_construct_voltage_tables(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to construct voltage tables!",
				result = tmp_result);
	}
	smum_initialize_mc_reg_table(hwmgr);

	if (phm_cap_enabled(hwmgr->platform_descriptor.platformCaps,
			PHM_PlatformCaps_EngineSpreadSpectrumSupport))
		PHM_WRITE_INDIRECT_FIELD(hwmgr->device, CGS_IND_REG__SMC,
				GENERAL_PWRMGT, DYN_SPREAD_SPECTRUM_EN, 1);

	if (phm_cap_enabled(hwmgr->platform_descriptor.platformCaps,
			PHM_PlatformCaps_ThermalController))
		PHM_WRITE_INDIRECT_FIELD(hwmgr->device, CGS_IND_REG__SMC,
				GENERAL_PWRMGT, THERMAL_PROTECTION_DIS, 0);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_program_static_screen_threshold_parameters(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to program static screen threshold parameters!",
			result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_display_gap(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable display gap!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_program_voting_clients(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to program voting clients!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smum_process_firmware_header(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to process firmware header!", result = tmp_result);

	if (hwmgr->chip_id != CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_initial_switch_from_arbf0_to_f1(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to initialize switch from ArbF0 to F1!",
				result = tmp_result);
	}

	result = PP_INIT_CALL(hwmgr, smu7_setup_default_dpm_tables(hwmgr));
	PP_ASSERT_WITH_CODE(0 == result,
			"Failed to setup default DPM tables!", return result);

	tmp_result = PP_INIT_CALL(hwmgr, smum_init_smc_table(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to initialize SMC table!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_vrhot_gpio_interrupt(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable VR hot GPIO interrupt!", result = tmp_result);

	if (hwmgr->chip_id >= CHIP_POLARIS10 &&
	    hwmgr->chip_id <= CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_notify_has_display(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to enable display setting!", result = tmp_result);
	} else {
		smum_send_msg_to_smc(hwmgr, (PPSMC_Msg)PPSMC_NoDisplay, NULL);
	}

	if (hwmgr->chip_id >= CHIP_POLARIS10 &&
	    hwmgr->chip_id <= CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_populate_edc_leakage_registers(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to populate edc leakage registers!", result = tmp_result);
	}

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_sclk_control(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable SCLK control!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_smc_voltage_controller(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable voltage control!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_ulv(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable ULV!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_deep_sleep_master_switch(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable deep sleep master switch!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_didt_config(hwmgr));
	PP_ASSERT_WITH_CODE((tmp_result == 0),
			"Failed to enable deep sleep master switch!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_start_dpm(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to start DPM!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_smc_cac(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable SMC CAC!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_power_containment(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable power containment!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_power_control_set_level(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to power control set level!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_thermal_auto_throttle(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable thermal auto throttle!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_pcie_performance_request(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"pcie performance request failed!", result = tmp_result);

	smu7_populate_umdpstate_clocks(hwmgr);

	return 0;
}
static int fixed_run(struct pp_hwmgr *hwmgr)
{
	int tmp_result = 0;
	int result = 0;

	if (smu7_voltage_control(hwmgr)) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_voltage_control(hwmgr));
		PP_ASSERT_WITH_CODE(tmp_result == 0,
				"Failed to enable voltage control!",
				result = tmp_result);

		tmp_result = PP_INIT_CALL(hwmgr, smu7_construct_voltage_tables(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to construct voltage tables!",
				result = tmp_result);
	}
	smum_initialize_mc_reg_table(hwmgr);

	if (phm_cap_enabled(hwmgr->platform_descriptor.platformCaps,
			PHM_PlatformCaps_EngineSpreadSpectrumSupport))
		PHM_WRITE_INDIRECT_FIELD(hwmgr->device, CGS_IND_REG__SMC,
				GENERAL_PWRMGT, DYN_SPREAD_SPECTRUM_EN, 1);

	if (phm_cap_enabled(hwmgr->platform_descriptor.platformCaps,
			PHM_PlatformCaps_ThermalController))
		PHM_WRITE_INDIRECT_FIELD(hwmgr->device, CGS_IND_REG__SMC,
				GENERAL_PWRMGT, THERMAL_PROTECTION_DIS, 0);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_program_static_screen_threshold_parameters(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to program static screen threshold parameters!",
			result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_display_gap(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable display gap!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_program_voting_clients(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to program voting clients!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smum_process_firmware_header(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to process firmware header!", result = tmp_result);

	if (hwmgr->chip_id != CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_initial_switch_from_arbf0_to_f1(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to initialize switch from ArbF0 to F1!",
				result = tmp_result);
	}

	result = PP_INIT_CALL(hwmgr, smu7_setup_default_dpm_tables(hwmgr));
	PP_ASSERT_WITH_CODE(0 == result,
			"Failed to setup default DPM tables!", return result);

	tmp_result = PP_INIT_CALL(hwmgr, smum_init_smc_table(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to initialize SMC table!", return tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_vrhot_gpio_interrupt(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable VR hot GPIO interrupt!", result = tmp_result);

	if (hwmgr->chip_id >= CHIP_POLARIS10 &&
	    hwmgr->chip_id <= CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_notify_has_display(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to enable display setting!", result = tmp_result);
	} else {
		smum_send_msg_to_smc(hwmgr, (PPSMC_Msg)PPSMC_NoDisplay, NULL);
	}

	if (hwmgr->chip_id >= CHIP_POLARIS10 &&
	    hwmgr->chip_id <= CHIP_VEGAM) {
		tmp_result = PP_INIT_CALL(hwmgr, smu7_populate_edc_leakage_registers(hwmgr));
		PP_ASSERT_WITH_CODE((0 == tmp_result),
				"Failed to populate edc leakage registers!", result = tmp_result);
	}

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_sclk_control(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable SCLK control!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_smc_voltage_controller(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable voltage control!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_ulv(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable ULV!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_deep_sleep_master_switch(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable deep sleep master switch!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_didt_config(hwmgr));
	PP_ASSERT_WITH_CODE((tmp_result == 0),
			"Failed to enable deep sleep master switch!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_start_dpm(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to start DPM!", return tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_smc_cac(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable SMC CAC!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_power_containment(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable power containment!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_power_control_set_level(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to power control set level!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_enable_thermal_auto_throttle(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"Failed to enable thermal auto throttle!", result = tmp_result);

	tmp_result = PP_INIT_CALL(hwmgr, smu7_pcie_performance_request(hwmgr));
	PP_ASSERT_WITH_CODE((0 == tmp_result),
			"pcie performance request failed!", result = tmp_result);

	smu7_populate_umdpstate_clocks(hwmgr);

	return 0;
}

int main(void){struct pp_hwmgr h={.chip_id=5};int r;
fail_table=1; late_calls=0; r=baseline_run(&h);
if(r!=0 || late_calls!=1)return 1;
late_calls=0;r=fixed_run(&h);if(r!=-5 || late_calls!=0)return 2;
fail_table=0;fail_dpm=1;late_calls=0;r=baseline_run(&h);
if(r!=0 || late_calls!=1)return 3;
late_calls=0;r=fixed_run(&h);if(r!=-22 || late_calls!=0)return 4;
fail_dpm=0;late_calls=0;r=fixed_run(&h);
if(r!=0 || late_calls!=1)return 5;
puts("PASS: baseline masks both faults; candidate propagates both and stops late calls; success path preserved");return 0;}
