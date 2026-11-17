# Output Relations

`output_model.csv`에서 XML을 만들 때 사용하는 논리적 output table 목록이다. 실제 DB 테이블이나 DDL을 정의하지 않는다.

- 모든 relation은 `<relation>_pk` 형식의 기술적 PK를 가진다.
- PK는 Input relation에서 자동 생성된 정수를 `input_output_model.sql`이 Output relation의 `<relation>_pk` 이름으로 가져온다.
- FK는 상위 relation의 PK를 전달받는 `integer` 열이며 이름은 `child_key`에 따른다.
- Input-to-output 변환 SQL은 `input_output_model.sql`에 두며, 이 문서는 relation 구조만 설명한다.

총 156개 relation, 741개 고유 열이다.

## globe_oecd

PK: `globe_oecd_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `globe_oecd_pk` | integer (generated) | PK |
| `version` | string (1..10 chars) | value |
| `sending_entity_in` | string (1..200 chars) | value |
| `transmitting_country` | enum (country_code) | value |
| `receiving_country` | enum (country_code) | value |
| `message_type` | enum (message_type) | value |
| `warning` | string (1..4000 chars) | value |
| `contact` | string (1..4000 chars) | value |
| `message_ref_id` | string (1..170 chars) | value |
| `message_type_indic` | enum (message_type_indic) | value |
| `reporting_period` | date | value |
| `timestamp` | dateTime | value |

## globe_body

PK: `globe_body_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `globe_body_pk` | integer (generated) | PK |
| `globe_oecd_pk` | integer | FK |

## filing_info

PK: `filing_info_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `filing_info_pk` | integer (generated) | PK |
| `globe_body_pk` | integer | FK |
| `name_mne` | string (1..200 chars) | value |
| `additional_info` | string (1..4000 chars) | value |

## general_section

PK: `general_section_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `general_section_pk` | integer (generated) | PK |
| `globe_body_pk` | integer | FK |
| `rec_jur_code` | enum (country_code) list | value |

## summary

PK: `summary_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `summary_pk` | integer (generated) | PK |
| `globe_body_pk` | integer | FK |
| `rec_jur_code` | enum (country_code) list | value |
| `safe_harbour` | enum (safe_harbour) list | value |
| `etr_range` | enum (etr_range) | value |
| `qdmt_tut` | enum (qdmt_tut) | value |
| `globe_tut` | enum (globe_tut) | value |

## jurisdiction_section

PK: `jurisdiction_section_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `jurisdiction_section_pk` | integer (generated) | PK |
| `globe_body_pk` | integer | FK |
| `rec_jur_code` | enum (country_code) list | value |
| `jurisdiction` | enum (country_code) | value |
| `local_currency` | enum (curr_code) | value |

## utpr_attribution

PK: `utpr_attribution_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `utpr_attribution_pk` | integer (generated) | PK |
| `globe_body_pk` | integer | FK |
| `rec_jur_code` | enum (country_code) list | value |

## filing_ce

PK: `filing_ce_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `filing_ce_pk` | integer (generated) | PK |
| `filing_info_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `name` | string (1..200 chars) | value |
| `role` | enum (filing_ce_role) | value |

## accounting_info

PK: `accounting_info_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `accounting_info_pk` | integer (generated) | PK |
| `filing_info_pk` | integer | FK |
| `cfs_of_upe` | enum (filing_ce_c_of_upe) | value |
| `fas` | string (1..200 chars) | value |
| `currency` | enum (curr_code) | value |

## period

PK: `period_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `period_pk` | integer (generated) | PK |
| `filing_info_pk` | integer | FK |
| `start` | date | value |
| `end` | date | value |

## doc_spec

PK: `doc_spec_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `doc_spec_pk` | integer (generated) | PK |
| `filing_info_pk` | integer | FK |
| `doc_type_indic` | enum (oecd_doc_type_indic) | value |
| `doc_ref_id` | string (1..200 chars) | value |
| `corr_doc_ref_id` | string (1..200 chars) | value |
| `general_section_pk` | integer | FK |
| `summary_pk` | integer | FK |
| `utpr_attribution_pk` | integer | FK |
| `jurisdiction_section_pk` | integer | FK |

## tin

PK: `tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `tin_pk` | integer (generated) | PK |
| `filing_ce_pk` | integer | FK |
| `tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |
| `excluded_upe_id_pk` | integer | FK |
| `other_upe_id_pk` | integer | FK |
| `ce_id_pk` | integer | FK |
| `pre_ownership_pk` | integer | FK |
| `ownership_pk` | integer | FK |
| `qiir_exception_pk` | integer | FK |
| `subgroup_pk` | integer | FK |
| `sub_group_pk` | integer | FK |
| `ce_computation_pk` | integer | FK |
| `entity_owner_pk` | integer | FK |
| `non_material_ce_id_pk` | integer | FK |
| `ltce_pk` | integer | FK |
| `parent_entity_pk` | integer | FK |

## corporate_structure

PK: `corporate_structure_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `corporate_structure_pk` | integer (generated) | PK |
| `general_section_pk` | integer | FK |
| `unreport_change_corp_str` | boolean | value |

## additional_data_point

PK: `additional_data_point_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `additional_data_point_pk` | integer (generated) | PK |
| `general_section_pk` | integer | FK |
| `description` | string (1..170 chars) | value |
| `amount` | integer | value |
| `percentage` | decimal | value |
| `text` | string (1..4000 chars) | value |
| `boolean` | boolean | value |
| `summary_pk` | integer | FK |
| `utpr_attribution_pk` | integer | FK |
| `jurisdiction_section_pk` | integer | FK |

## upe

PK: `upe_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `upe_pk` | integer (generated) | PK |
| `corporate_structure_pk` | integer | FK |

## ce

PK: `ce_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ce_pk` | integer (generated) | PK |
| `corporate_structure_pk` | integer | FK |

## excluded_entity

PK: `excluded_entity_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `excluded_entity_pk` | integer (generated) | PK |
| `corporate_structure_pk` | integer | FK |
| `name` | string (1..200 chars) | value |
| `type` | enum (excluded_entity) | value |
| `change` | boolean | value |

## excluded_upe

PK: `excluded_upe_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `excluded_upe_pk` | integer (generated) | PK |
| `upe_pk` | integer | FK |
| `excluded_upe_status` | enum (excluded_upe) | value |
| `art_10_3_5` | enum (country_code) | value |

## other_upe

PK: `other_upe_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `other_upe_pk` | integer (generated) | PK |
| `upe_pk` | integer | FK |
| `art_10_3_5` | enum (country_code) | value |

## excluded_upe_id

PK: `excluded_upe_id_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `excluded_upe_id_pk` | integer (generated) | PK |
| `excluded_upe_pk` | integer | FK |
| `name` | string (1..200 chars) | value |
| `res_country_code` | enum (country_code) list | value |
| `rules` | enum (id_type_rules) list | value |
| `globe_status` | enum (id_type_globe_status) list | value |

## other_upe_id

PK: `other_upe_id_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `other_upe_id_pk` | integer (generated) | PK |
| `other_upe_pk` | integer | FK |
| `name` | string (1..200 chars) | value |
| `res_country_code` | enum (country_code) list | value |
| `rules` | enum (id_type_rules) list | value |
| `globe_status` | enum (id_type_globe_status) list | value |

## ce_id

PK: `ce_id_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ce_id_pk` | integer (generated) | PK |
| `ce_pk` | integer | FK |
| `name` | string (1..200 chars) | value |
| `res_country_code` | enum (country_code) list | value |
| `rules` | enum (id_type_rules) list | value |
| `globe_status` | enum (id_type_globe_status) list | value |

## ownership_change

PK: `ownership_change_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ownership_change_pk` | integer (generated) | PK |
| `ce_pk` | integer | FK |
| `change_date` | date | value |
| `pre_globe_status` | enum (id_globe_status) list | value |

## ownership

PK: `ownership_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ownership_pk` | integer (generated) | PK |
| `ce_pk` | integer | FK |
| `ownership_type` | enum (ownership_type) | value |
| `ownership_percentage` | decimal | value |

## qiir

PK: `qiir_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qiir_pk` | integer (generated) | PK |
| `ce_pk` | integer | FK |
| `pope_ipe` | enum (pope_ipe) | value |

## qutpr

PK: `qutpr_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qutpr_pk` | integer (generated) | PK |
| `ce_pk` | integer | FK |
| `art_9_3` | boolean | value |
| `agg_ownership` | decimal | value |
| `upe_ownership` | boolean | value |

## pre_ownership

PK: `pre_ownership_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `pre_ownership_pk` | integer (generated) | PK |
| `ownership_change_pk` | integer | FK |
| `ownership_type` | enum (ownership_type) | value |
| `pre_ownership_percentage` | decimal | value |

## qiir_exception

PK: `qiir_exception_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qiir_exception_pk` | integer (generated) | PK |
| `qiir_pk` | integer | FK |

## qiir_exception_rule

PK: `qiir_exception_rule_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qiir_exception_rule_pk` | integer (generated) | PK |
| `qiir_exception_pk` | integer | FK |
| `art_2_1_3` | boolean | value |
| `art_2_1_5` | boolean | value |

## jurisdiction

PK: `jurisdiction_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `jurisdiction_pk` | integer (generated) | PK |
| `summary_pk` | integer | FK |
| `jurisdiction_name` | enum (country_code) | value |

## subgroup

PK: `subgroup_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `subgroup_pk` | integer (generated) | PK |
| `jurisdiction_pk` | integer | FK |
| `type_of_sub_group` | enum (type_of_sub_group) list | value |
| `jur_with_taxing_rights_pk` | integer | FK |

## jur_with_taxing_rights

PK: `jur_with_taxing_rights_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `jur_with_taxing_rights_pk` | integer (generated) | PK |
| `summary_pk` | integer | FK |
| `jurisdiction_name` | enum (country_code) | value |
| `diff_domestic_tut` | enum (globe_tut) | value |
| `jurisdiction_section_pk` | integer | FK |

## sbie

PK: `sbie_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `sbie_pk` | integer (generated) | PK |
| `summary_pk` | integer | FK |
| `not_applicable` | boolean | value |
| `no_tut` | boolean | value |

## attribution

PK: `attribution_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `attribution_pk` | integer (generated) | PK |
| `utpr_attribution_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `utpr_top_up_tax_carry_forward` | integer | value |
| `employees` | integer | value |
| `tangible_asset_value` | integer | value |
| `utpr_percentage` | decimal | value |
| `utpr_top_up_tax_attributed` | integer | value |
| `add_cash_tax_expense` | integer | value |
| `utpr_top_up_tax_carried_forward` | integer | value |

## globe_tax

PK: `globe_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `globe_tax_pk` | integer (generated) | PK |
| `jurisdiction_section_pk` | integer | FK |

## low_tax_jurisdiction

PK: `low_tax_jurisdiction_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `low_tax_jurisdiction_pk` | integer (generated) | PK |
| `jurisdiction_section_pk` | integer | FK |
| `top_up_tax_amount` | integer | value |

## report_difference

PK: `report_difference_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `report_difference_pk` | integer (generated) | PK |
| `jur_with_taxing_rights_pk` | integer | FK |
| `etr_difference` | decimal | value |
| `net_globe_difference` | integer | value |
| `sbie_difference` | integer | value |
| `add_current_tut_difference` | integer | value |
| `tut_difference` | integer | value |
| `elections_difference` | string (1..4000 chars) | value |
| `qrtc_income` | integer | value |
| `excess_neg_tax_carry_forw` | integer | value |
| `transition_difference` | boolean | value |

## adj_covered_tax_difference

PK: `adj_covered_tax_difference_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adj_covered_tax_difference_pk` | integer (generated) | PK |
| `report_difference_pk` | integer | FK |
| `agg_current_tax_expense` | integer | value |
| `qrtc_expense` | integer | value |
| `other_tax_credits` | integer | value |
| `defer_tax_expense` | integer | value |

## etr

PK: `etr_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `etr_pk` | integer (generated) | PK |
| `globe_tax_pk` | integer | FK |

## initial_int_activity

PK: `initial_int_activity_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `initial_int_activity_pk` | integer (generated) | PK |
| `globe_tax_pk` | integer | FK |
| `start_date` | date | value |
| `rfy_number_of_jurisdictions` | integer | value |
| `rfy_sum_tangible_asset_value` | integer | value |

## sub_group

PK: `sub_group_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `sub_group_pk` | integer (generated) | PK |
| `etr_pk` | integer | FK |
| `type_of_sub_group` | enum (etr_type_of_sub_group) list | value |

## etr_status

PK: `etr_status_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `etr_status_pk` | integer (generated) | PK |
| `etr_pk` | integer | FK |

## etr_election

PK: `etr_election_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `etr_election_pk` | integer (generated) | PK |
| `etr_pk` | integer | FK |
| `art_3_2_6` | boolean | value |
| `art_4_1_5` | boolean | value |
| `art_4_6_1` | boolean | value |
| `art_5_3_1` | boolean | value |
| `simplified_reporting` | boolean | value |

## reference_jurisdiction

PK: `reference_jurisdiction_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `reference_jurisdiction_pk` | integer (generated) | PK |
| `initial_int_activity_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `tangible_asset_value` | integer | value |

## other_jurisdiction

PK: `other_jurisdiction_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `other_jurisdiction_pk` | integer (generated) | PK |
| `initial_int_activity_pk` | integer | FK |
| `res_country_code` | enum (country_code) list | value |
| `tangible_asset_value` | integer | value |

## etr_exception

PK: `etr_exception_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `etr_exception_pk` | integer (generated) | PK |
| `etr_status_pk` | integer | FK |

## etr_computation

PK: `etr_computation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `etr_computation_pk` | integer (generated) | PK |
| `etr_status_pk` | integer | FK |

## art_3_2_2

PK: `art_3_2_2_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_2_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_3_2_5

PK: `art_3_2_5_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_5_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_3_2_8

PK: `art_3_2_8_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_8_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## no_def_tax_allocation

PK: `no_def_tax_allocation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `no_def_tax_allocation_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_4_5

PK: `art_4_5_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_4_5_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_3_2_1_c

PK: `art_3_2_1_c_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_1_c_pk` | integer (generated) | PK |
| `etr_election_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |
| `qual_owner_intent_balance` | integer | value |
| `additions` | integer | value |
| `reductions` | integer | value |
| `outstanding_balance` | integer | value |

## deminimis_simplified_nmce_calc

PK: `deminimis_simplified_nmce_calc_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `deminimis_simplified_nmce_calc_pk` | integer (generated) | PK |
| `etr_exception_pk` | integer | FK |
| `basis` | enum (deminimis_simple_basis) | value |

## transitional_cb_cr_safe_harbour

PK: `transitional_cb_cr_safe_harbour_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `transitional_cb_cr_safe_harbour_pk` | integer (generated) | PK |
| `etr_exception_pk` | integer | FK |
| `revenue` | integer | value |
| `profit` | integer | value |
| `income_tax` | integer | value |

## utpr_safe_harbour

PK: `utpr_safe_harbour_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `utpr_safe_harbour_pk` | integer (generated) | PK |
| `etr_exception_pk` | integer | FK |
| `cit_rate` | decimal | value |

## financial_data

PK: `financial_data_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `financial_data_pk` | integer (generated) | PK |
| `deminimis_simplified_nmce_calc_pk` | integer | FK |
| `year` | date | value |
| `revenue` | integer | value |
| `globe_revenue` | integer | value |
| `net_globe_income` | integer | value |
| `fanil` | integer | value |

## average

PK: `average_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `average_pk` | integer (generated) | PK |
| `deminimis_simplified_nmce_calc_pk` | integer | FK |
| `revenue` | integer | value |
| `globe_revenue` | integer | value |
| `net_globe_income` | integer | value |
| `fanil` | integer | value |

## ce_computation

PK: `ce_computation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ce_computation_pk` | integer (generated) | PK |
| `etr_computation_pk` | integer | FK |
| `other_fas` | string (1..200 chars) | value |

## overall_computation

PK: `overall_computation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_pk` | integer (generated) | PK |
| `etr_computation_pk` | integer | FK |
| `fanil` | integer | value |
| `adjusted_fanil` | integer | value |
| `income_tax_expense` | integer | value |
| `etr_rate` | decimal | value |
| `top_up_tax_percentage` | decimal | value |
| `excess_profits` | integer | value |
| `top_up_tax` | integer | value |

## non_material_ce

PK: `non_material_ce_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `non_material_ce_pk` | integer (generated) | PK |
| `etr_computation_pk` | integer | FK |

## adjusted_fanil

PK: `adjusted_fanil_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjusted_fanil_pk` | integer (generated) | PK |
| `ce_computation_pk` | integer | FK |
| `total` | integer | value |
| `fanil` | integer | value |

## net_globe_income

PK: `net_globe_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `net_globe_income_pk` | integer (generated) | PK |
| `ce_computation_pk` | integer | FK |
| `total` | integer | value |

## adjusted_income_tax

PK: `adjusted_income_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjusted_income_tax_pk` | integer (generated) | PK |
| `ce_computation_pk` | integer | FK |
| `total` | integer | value |
| `income_tax` | integer | value |

## adjusted_covered_tax

PK: `adjusted_covered_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjusted_covered_tax_pk` | integer (generated) | PK |
| `ce_computation_pk` | integer | FK |
| `total` | integer | value |

## elections

PK: `elections_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `elections_pk` | integer (generated) | PK |
| `ce_computation_pk` | integer | FK |
| `simpl_calculations` | boolean | value |
| `art_3_2_1` | boolean | value |

## overall_computation_net_globe_income

PK: `overall_computation_net_globe_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_net_globe_income_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |
| `total` | integer | value |

## overall_computation_adjusted_covered_tax

PK: `overall_computation_adjusted_covered_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_adjusted_covered_tax_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |
| `total` | integer | value |
| `aggregrate_current_tax` | integer | value |

## overall_computation_substance_exclusion

PK: `overall_computation_substance_exclusion_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_substance_exclusion_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |
| `total` | integer | value |
| `payroll_cost` | integer | value |
| `payroll_mark_up` | decimal | value |
| `tangible_asset_value` | integer | value |
| `tangible_asset_markup` | decimal | value |

## additional_top_up_tax

PK: `additional_top_up_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `additional_top_up_tax_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |

## qdmtt

PK: `qdmtt_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qdmtt_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |
| `fas` | string (1..200 chars) | value |
| `amount` | integer | value |
| `min_rate` | decimal | value |
| `basisfor_blending` | string (1..4000 chars) | value |
| `sbie_available` | boolean | value |
| `de_min_available` | boolean | value |
| `currency` | enum (curr_code) | value |

## excess_neg_tax_expense

PK: `excess_neg_tax_expense_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `excess_neg_tax_expense_pk` | integer (generated) | PK |
| `overall_computation_pk` | integer | FK |
| `prior_year_balance` | integer | value |
| `generated_in_rfy` | integer | value |
| `utilized_in_rfy` | integer | value |
| `remaining` | integer | value |

## rfy

PK: `rfy_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `rfy_pk` | integer (generated) | PK |
| `non_material_ce_pk` | integer | FK |
| `total_revenue` | integer | value |
| `aggregate_simplified` | integer | value |

## rfy_1

PK: `rfy_1_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `rfy_1_pk` | integer (generated) | PK |
| `non_material_ce_pk` | integer | FK |
| `total_revenue` | integer | value |

## rfy_2

PK: `rfy_2_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `rfy_2_pk` | integer (generated) | PK |
| `non_material_ce_pk` | integer | FK |
| `total_revenue` | integer | value |

## non_material_ce_average

PK: `non_material_ce_average_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `non_material_ce_average_pk` | integer (generated) | PK |
| `non_material_ce_pk` | integer | FK |
| `total_revenue` | integer | value |

## non_material_ce_id

PK: `non_material_ce_id_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `non_material_ce_id_pk` | integer (generated) | PK |
| `non_material_ce_pk` | integer | FK |
| `name` | string (1..200 chars) | value |
| `res_country_code` | enum (country_code) list | value |
| `rules` | enum (id_type_rules) list | value |
| `globe_status` | enum (id_type_globe_status) list | value |

## adjustment

PK: `adjustment_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjustment_pk` | integer (generated) | PK |
| `adjusted_fanil_pk` | integer | FK |

## adjustments

PK: `adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjustments_pk` | integer (generated) | PK |
| `net_globe_income_pk` | integer | FK |
| `amount` | integer list | value |
| `adjustment_item` | enum (adjustment_item) | value |

## int_shipping_income

PK: `int_shipping_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `int_shipping_income_pk` | integer (generated) | PK |
| `net_globe_income_pk` | integer | FK |
| `covered_taxes` | integer | value |

## cross_allocation

PK: `cross_allocation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `cross_allocation_pk` | integer (generated) | PK |
| `adjusted_income_tax_pk` | integer | FK |
| `basis` | enum (adjusted_basis) list | value |
| `res_country_code` | enum (country_code) | value |
| `additions` | integer | value |
| `reductions` | integer | value |

## adjusted_covered_tax_adjustments

PK: `adjusted_covered_tax_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `adjusted_covered_tax_adjustments_pk` | integer (generated) | PK |
| `adjusted_covered_tax_pk` | integer | FK |
| `amount` | integer list | value |
| `adjustment_item` | enum (current_adjusted_tax) | value |

## defer_tax_adjust_amt

PK: `defer_tax_adjust_amt_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `defer_tax_adjust_amt_pk` | integer (generated) | PK |
| `adjusted_covered_tax_pk` | integer | FK |
| `total` | integer | value |
| `defer_tax_expense` | integer | value |

## art_1_5_3

PK: `art_1_5_3_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_1_5_3_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_3_2_1b

PK: `art_3_2_1b_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_1b_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_3_2_1c

PK: `art_3_2_1c_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_3_2_1c_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_6_3_4

PK: `art_6_3_4_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_6_3_4_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `fy_trigger_event` | date | value |

## aggregated_reporting

PK: `aggregated_reporting_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `aggregated_reporting_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |

## art_4_4_7

PK: `art_4_4_7_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_4_4_7_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_4_5_6

PK: `art_4_5_6_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_4_5_6_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_7_5

PK: `art_7_5_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_7_5_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |

## art_7_6

PK: `art_7_6_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_7_6_pk` | integer (generated) | PK |
| `elections_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |
| `actual_deemed_dist` | integer | value |
| `local_creditable_tax_gross` | integer | value |
| `share_of_undist_net_globe_inc` | decimal | value |

## main_entity_p_eand_fte

PK: `main_entity_p_eand_fte_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `main_entity_p_eand_fte_pk` | integer (generated) | PK |
| `adjustment_pk` | integer | FK |
| `basis` | enum (main_entity_p_eand_fte_basis) | value |
| `res_country_code` | enum (country_code) | value |
| `additions` | integer | value |
| `reductions` | integer | value |

## cross_border_adjustments

PK: `cross_border_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `cross_border_adjustments_pk` | integer (generated) | PK |
| `adjustment_pk` | integer | FK |
| `basis` | enum (cross_border_adjustments) | value |
| `res_country_code` | enum (country_code) | value |
| `additions` | integer | value |
| `reductions` | integer | value |

## upe_adjustments

PK: `upe_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `upe_adjustments_pk` | integer (generated) | PK |
| `adjustment_pk` | integer | FK |
| `basis` | enum (upe_adjustments_basis) | value |

## other_tin

PK: `other_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `other_tin_pk` | integer (generated) | PK |
| `main_entity_p_eand_fte_pk` | integer | FK |
| `other_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## cross_border_adjustments_other_tin

PK: `cross_border_adjustments_other_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `cross_border_adjustments_other_tin_pk` | integer (generated) | PK |
| `cross_border_adjustments_pk` | integer | FK |
| `other_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## reductions

PK: `reductions_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `reductions_pk` | integer (generated) | PK |
| `upe_adjustments_pk` | integer | FK |
| `amount` | integer | value |
| `exception` | boolean | value |

## identification_of_owners

PK: `identification_of_owners_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `identification_of_owners_pk` | integer (generated) | PK |
| `upe_adjustments_pk` | integer | FK |
| `ownership_percentage` | decimal | value |

## ind_owners

PK: `ind_owners_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ind_owners_pk` | integer (generated) | PK |
| `identification_of_owners_pk` | integer | FK |
| `num_of_owners` | integer | value |
| `res_country_code` | enum (country_code) | value |
| `tax_rate` | decimal | value |

## entity_owner

PK: `entity_owner_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `entity_owner_pk` | integer (generated) | PK |
| `identification_of_owners_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `tax_rate` | decimal | value |
| `ex_type_of_entity` | enum (ex_type_of_entity) | value |

## international_ship_income

PK: `international_ship_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `international_ship_income_pk` | integer (generated) | PK |
| `int_shipping_income_pk` | integer | FK |
| `total` | integer | value |
| `category` | enum (int_ship_category) list | value |
| `revenue` | integer | value |
| `costs` | integer | value |

## qualified_anc_ship_income

PK: `qualified_anc_ship_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `qualified_anc_ship_income_pk` | integer (generated) | PK |
| `int_shipping_income_pk` | integer | FK |
| `total` | integer | value |
| `category` | enum (anc_ship_category) | value |
| `revenue` | integer | value |
| `costs` | integer | value |

## substance_exclusion

PK: `substance_exclusion_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `substance_exclusion_pk` | integer (generated) | PK |
| `int_shipping_income_pk` | integer | FK |
| `payroll_costs` | integer | value |
| `tangible_assets` | integer | value |

## cross_allocation_other_tin

PK: `cross_allocation_other_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `cross_allocation_other_tin_pk` | integer (generated) | PK |
| `cross_allocation_pk` | integer | FK |
| `other_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## defer_tax_adjust_amt_adjustment

PK: `defer_tax_adjust_amt_adjustment_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `defer_tax_adjust_amt_adjustment_pk` | integer (generated) | PK |
| `defer_tax_adjust_amt_pk` | integer | FK |
| `amount` | integer list | value |
| `adjustment_item` | enum (deferred_adjusted_tax) | value |

## recast

PK: `recast_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `recast_pk` | integer (generated) | PK |
| `defer_tax_adjust_amt_adjustment_pk` | integer | FK |
| `higher` | integer | value |
| `lower` | integer | value |

## inclusion

PK: `inclusion_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `inclusion_pk` | integer (generated) | PK |
| `art_6_3_4_pk` | integer | FK |
| `art_6_3_4_c_i` | boolean | value |
| `art_6_3_4_c_ii` | boolean | value |

## tax_consol_group_tin

PK: `tax_consol_group_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `tax_consol_group_tin_pk` | integer (generated) | PK |
| `aggregated_reporting_pk` | integer | FK |
| `tax_consol_group_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## entity_tin

PK: `entity_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `entity_tin_pk` | integer (generated) | PK |
| `aggregated_reporting_pk` | integer | FK |
| `entity_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## ce_owner_tin

PK: `ce_owner_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ce_owner_tin_pk` | integer (generated) | PK |
| `art_7_5_pk` | integer | FK |
| `ce_owner_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## investment_entity_tin

PK: `investment_entity_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `investment_entity_tin_pk` | integer (generated) | PK |
| `art_7_6_pk` | integer | FK |
| `investment_entity_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## overall_computation_net_globe_income_adjustments

PK: `overall_computation_net_globe_income_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_net_globe_income_adjustments_pk` | integer (generated) | PK |
| `overall_computation_net_globe_income_pk` | integer | FK |
| `amount` | integer | value |
| `adjustment_item` | enum (adjustment_item) | value |

## overall_computation_net_globe_income_int_shipping_income

PK: `overall_computation_net_globe_income_int_shipping_income_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_net_globe_income_int_shipping_income_pk` | integer (generated) | PK |
| `overall_computation_net_globe_income_pk` | integer | FK |
| `total` | integer | value |
| `total_int_ship_income` | integer | value |
| `fifty_percent_cap` | integer | value |
| `total_qualified_anc_income` | integer | value |
| `excess_of_cap` | integer | value |

## overall_computation_adjusted_covered_tax_adjustments

PK: `overall_computation_adjusted_covered_tax_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_adjusted_covered_tax_adjustments_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_pk` | integer | FK |
| `amount` | integer | value |
| `adjustment_item` | enum (final_adjusted_tax) | value |

## post_filing_adjust

PK: `post_filing_adjust_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `post_filing_adjust_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_pk` | integer | FK |

## defer_tax_asset

PK: `defer_tax_asset_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `defer_tax_asset_pk` | integer (generated) | PK |
| `post_filing_adjust_pk` | integer | FK |
| `total` | integer | value |

## amount_attributed

PK: `amount_attributed_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `amount_attributed_pk` | integer (generated) | PK |
| `defer_tax_asset_pk` | integer | FK |
| `year` | date | value |
| `amount` | integer | value |

## covered_tax_refund

PK: `covered_tax_refund_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `covered_tax_refund_pk` | integer (generated) | PK |
| `post_filing_adjust_pk` | integer | FK |
| `total` | integer | value |

## covered_tax_refund_amount_attributed

PK: `covered_tax_refund_amount_attributed_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `covered_tax_refund_amount_attributed_pk` | integer (generated) | PK |
| `covered_tax_refund_pk` | integer | FK |
| `year` | date | value |
| `amount` | integer | value |

## deemed_dist_tax

PK: `deemed_dist_tax_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `deemed_dist_tax_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_pk` | integer | FK |
| `total` | integer | value |

## election

PK: `election_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `election_pk` | integer (generated) | PK |
| `deemed_dist_tax_pk` | integer | FK |
| `reduction` | integer | value |
| `incremental_top_up_tax` | integer | value |
| `ratio` | decimal | value |

## recapture

PK: `recapture_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `recapture_pk` | integer (generated) | PK |
| `election_pk` | integer | FK |
| `year` | date | value |
| `start_amount` | integer | value |
| `ddt_year_0` | integer | value |
| `ddt_year_1` | integer | value |
| `ddt_year_2` | integer | value |
| `ddt_year_3` | integer | value |
| `total_ddt` | integer | value |
| `end_amount` | integer | value |

## overall_computation_adjusted_covered_tax_defer_tax_adjust_amt

PK: `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_pk` | integer | FK |
| `total` | integer | value |
| `def_tax_amt` | integer | value |
| `diff_carry_value` | integer | value |
| `globe_value` | integer | value |
| `bef_recast_adjust` | integer | value |
| `total_adjust` | integer | value |
| `pre_recast` | integer | value |

## overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_recast

PK: `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_recast_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_recast_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_pk` | integer | FK |
| `higher` | integer | value |
| `lower` | integer | value |

## overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_adjustments

PK: `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_adjustments_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_adjustments_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_pk` | integer | FK |
| `amount` | integer | value |
| `adjustment_item` | enum (deferred_adjusted_tax) | value |

## recapture_deferred

PK: `recapture_deferred_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `recapture_deferred_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_adjustments_pk` | integer | FK |
| `dtlrfy_minus_5` | integer | value |
| `recap_dtlrfy_minus_5` | integer | value |
| `dtlrfy` | integer | value |

## aggregate_dtl

PK: `aggregate_dtl_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `aggregate_dtl_pk` | integer (generated) | PK |
| `recapture_deferred_pk` | integer | FK |

## reporting_fiscal_year

PK: `reporting_fiscal_year_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `reporting_fiscal_year_pk` | integer (generated) | PK |
| `aggregate_dtl_pk` | integer | FK |
| `amount_pre_transition` | integer | value |
| `amount_out_balance` | integer | value |
| `amount_unjustified` | integer | value |

## prior_fiscal_year

PK: `prior_fiscal_year_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `prior_fiscal_year_pk` | integer (generated) | PK |
| `aggregate_dtl_pk` | integer | FK |
| `amount_pre_transition` | integer | value |
| `amount_out_balance` | integer | value |
| `amount_unjustified` | integer | value |

## transition

PK: `transition_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `transition_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_defer_tax_adjust_amt_pk` | integer | FK |
| `year` | date | value |
| `deferred_tax_liability_start` | integer | value |
| `deferred_tax_liability_recast` | integer | value |
| `alt_jurisdiction` | enum (country_code) | value |

## deferred_tax_assets

PK: `deferred_tax_assets_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `deferred_tax_assets_pk` | integer (generated) | PK |
| `transition_pk` | integer | FK |
| `total` | integer | value |
| `deferred_tax_asset_start` | integer | value |
| `deferred_tax_asset_recast` | integer | value |
| `deferred_tax_asset_excluded` | integer | value |

## disposal

PK: `disposal_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `disposal_pk` | integer (generated) | PK |
| `transition_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `net_dtadtl` | integer | value |
| `carrying_value` | integer | value |
| `tax_paid` | integer | value |
| `dtadtl` | integer | value |

## trans_blend_cfc

PK: `trans_blend_cfc_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `trans_blend_cfc_pk` | integer (generated) | PK |
| `overall_computation_adjusted_covered_tax_pk` | integer | FK |
| `total` | integer | value |

## cfc_jur

PK: `cfc_jur_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `cfc_jur_pk` | integer (generated) | PK |
| `trans_blend_cfc_pk` | integer | FK |
| `jurisdiction` | enum (country_code) | value |

## allocation

PK: `allocation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `allocation_pk` | integer (generated) | PK |
| `cfc_jur_pk` | integer | FK |
| `agg_alloc_tax` | integer | value |

## sub_group_tin

PK: `sub_group_tin_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `sub_group_tin_pk` | integer (generated) | PK |
| `allocation_pk` | integer | FK |
| `sub_group_tin_value` | string (1..200 chars) | value |
| `issued_by` | enum (country_code) | value |
| `unknown` | boolean | value |
| `type_of_tin` | enum (type_of_tin) | value |

## pe_allocation

PK: `pe_allocation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `pe_allocation_pk` | integer (generated) | PK |
| `overall_computation_substance_exclusion_pk` | integer | FK |

## jur_of_owners

PK: `jur_of_owners_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `jur_of_owners_pk` | integer (generated) | PK |
| `pe_allocation_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `upe` | boolean | value |
| `not_applicable` | boolean | value |

## payroll_cost

PK: `payroll_cost_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `payroll_cost_pk` | integer (generated) | PK |
| `pe_allocation_pk` | integer | FK |
| `total` | integer | value |
| `allocation` | integer | value |

## tangible_asset_value

PK: `tangible_asset_value_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `tangible_asset_value_pk` | integer (generated) | PK |
| `pe_allocation_pk` | integer | FK |
| `total` | integer | value |
| `allocation` | integer | value |

## fte_allocation

PK: `fte_allocation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `fte_allocation_pk` | integer (generated) | PK |
| `overall_computation_substance_exclusion_pk` | integer | FK |

## fte_allocation_jur_of_owners

PK: `fte_allocation_jur_of_owners_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `fte_allocation_jur_of_owners_pk` | integer (generated) | PK |
| `fte_allocation_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `upe` | boolean | value |
| `not_applicable` | boolean | value |

## fte_allocation_payroll_cost

PK: `fte_allocation_payroll_cost_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `fte_allocation_payroll_cost_pk` | integer (generated) | PK |
| `fte_allocation_pk` | integer | FK |
| `total` | integer | value |
| `allocation` | integer | value |

## fte_allocation_tangible_asset_value

PK: `fte_allocation_tangible_asset_value_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `fte_allocation_tangible_asset_value_pk` | integer (generated) | PK |
| `fte_allocation_pk` | integer | FK |
| `total` | integer | value |
| `allocation` | integer | value |

## non_art_4_1_5

PK: `non_art_4_1_5_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `non_art_4_1_5_pk` | integer (generated) | PK |
| `additional_top_up_tax_pk` | integer | FK |
| `articles` | enum (non_art_415) list | value |
| `year` | date | value |
| `additional_top_up_tax` | integer | value |

## previous

PK: `previous_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `previous_pk` | integer (generated) | PK |
| `non_art_4_1_5_pk` | integer | FK |
| `net_globe_income` | integer | value |
| `adjusted_covered_tax` | integer | value |
| `etr_rate` | decimal | value |
| `excess_profits` | integer | value |
| `top_up_tax_percentage` | decimal | value |
| `top_up_tax` | integer | value |

## recalculated

PK: `recalculated_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `recalculated_pk` | integer (generated) | PK |
| `non_art_4_1_5_pk` | integer | FK |
| `net_globe_income` | integer | value |
| `adjusted_covered_tax` | integer | value |
| `etr_rate` | decimal | value |
| `excess_profits` | integer | value |
| `top_up_tax_percentage` | decimal | value |
| `top_up_tax` | integer | value |

## art_4_1_5

PK: `art_4_1_5_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `art_4_1_5_pk` | integer (generated) | PK |
| `additional_top_up_tax_pk` | integer | FK |
| `adjusted_covered_tax` | integer | value |
| `globe_loss` | integer | value |
| `expected_adjusted_covered_tax` | integer | value |
| `additional_top_up_tax` | integer | value |

## currency_election

PK: `currency_election_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `currency_election_pk` | integer (generated) | PK |
| `qdmtt_pk` | integer | FK |
| `status` | boolean | value |
| `election_year` | date | value |
| `revocation_year` | date | value |
| `currency` | enum (currency) | value |

## ltce

PK: `ltce_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `ltce_pk` | integer (generated) | PK |
| `low_tax_jurisdiction_pk` | integer | FK |

## iir

PK: `iir_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `iir_pk` | integer (generated) | PK |
| `ltce_pk` | integer | FK |
| `net_globe_income` | integer | value |
| `top_up_tax` | integer | value |

## parent_entity

PK: `parent_entity_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `parent_entity_pk` | integer (generated) | PK |
| `iir_pk` | integer | FK |
| `res_country_code` | enum (country_code) | value |
| `other_ownership_allocation` | integer | value |
| `inclusion_ratio` | decimal | value |
| `top_up_tax_share` | integer | value |
| `iir_off_set` | integer | value |
| `top_up_tax` | integer | value |

## utpr

PK: `utpr_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `utpr_pk` | integer (generated) | PK |
| `low_tax_jurisdiction_pk` | integer | FK |

## utpr_utpr_safe_harbour

PK: `utpr_utpr_safe_harbour_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `utpr_utpr_safe_harbour_pk` | integer (generated) | PK |
| `utpr_pk` | integer | FK |
| `cit_rate` | decimal | value |

## utpr_calculation

PK: `utpr_calculation_pk`

| Column | Data type | Role |
| --- | --- | --- |
| `utpr_calculation_pk` | integer (generated) | PK |
| `utpr_pk` | integer | FK |
| `total_utpr_top_up_tax` | integer | value |
| `article_2_5_1_top_up_tax` | integer | value |
