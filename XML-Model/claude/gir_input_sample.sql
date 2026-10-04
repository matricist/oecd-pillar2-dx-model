-- GIR 정규화 입력 모델 (샘플). SQLite 문법. BOOLEAN=0/1, DATE=ISO 문자열

-- 다국적기업 그룹. 보고서 1건의 뼈대
CREATE TABLE mne_group (
  group_id                    TEXT,
  name                        TEXT,
  upe_entity_id               TEXT,
  cfs_of_upe                  TEXT,
  fas                         TEXT,
  currency                    TEXT,
  period_start                TEXT,
  period_end                  TEXT
);

-- 메시지(제출) 1건. 같은 그룹을 다른 수신국에 다시 보내면 행이 늘어남
CREATE TABLE filing (
  filing_id                   TEXT,
  group_id                    TEXT,
  message_ref_id              TEXT,
  transmitting_country        TEXT,
  receiving_country           TEXT,
  message_type_indic          TEXT,
  reporting_period            TEXT,
  sent_at                     TEXT,
  sending_entity_in           TEXT,
  contact                     TEXT,
  filing_entity_id            TEXT,
  filing_role                 TEXT,
  additional_info             TEXT,
  unreported_change_corp_str  INTEGER,
  schema_version              TEXT
);

-- 구성기업 마스터. XSD에서 ID_Type이 나오는 모든 자리(UPE, CE, Non-MaterialCE)와 23개의 TIN 참조가 전부 여기를 가리킴
CREATE TABLE entity (
  entity_id                   TEXT,
  group_id                    TEXT,
  name                        TEXT,
  main_country                TEXT,
  is_upe                      INTEGER,
  excluded_upe_status         TEXT,
  art_10_3_5_country          TEXT,
  is_non_material             INTEGER,
  pope_ipe                    TEXT,
  qiir_exception_rule         TEXT,
  qiir_exception_entity_id    TEXT,
  qutpr_art9_3                INTEGER,
  qutpr_agg_ownership         REAL,
  qutpr_upe_ownership         INTEGER,
  other_fas                   TEXT
);

-- 기업별 TIN. 1..n
CREATE TABLE entity_tin (
  entity_id                   TEXT,
  ord                         INTEGER,
  tin                         TEXT,
  issued_by                   TEXT,
  tin_type                    TEXT,
  unknown                     INTEGER
);

-- 기업별 소재 관할국. 1..n
CREATE TABLE entity_country (
  entity_id                   TEXT,
  ord                         INTEGER,
  country                     TEXT
);

-- 적용 규칙. 1..n
CREATE TABLE entity_rule (
  entity_id                   TEXT,
  ord                         INTEGER,
  rule                        TEXT
);

-- GloBE 상 지위. 1..n
CREATE TABLE entity_globe_status (
  entity_id                   TEXT,
  ord                         INTEGER,
  status                      TEXT
);

-- 소유 관계. 피소유 기업 기준 1..n
CREATE TABLE ownership (
  owned_entity_id             TEXT,
  ord                         INTEGER,
  ownership_type              TEXT,
  owner_entity_id             TEXT,
  percentage                  REAL
);

-- 제외실체 목록
CREATE TABLE excluded_entity (
  group_id                    TEXT,
  ord                         INTEGER,
  name                        TEXT,
  type                        TEXT,
  changed                     INTEGER
);

-- 관할국별 요약과 섹션 헤더. 그룹×관할국 1행
CREATE TABLE jurisdiction (
  group_id                    TEXT,
  jur_code                    TEXT,
  local_currency              TEXT,
  etr_range                   TEXT,
  sbie_not_applicable         INTEGER,
  sbie_no_tut                 INTEGER,
  qdmtt_tut                   TEXT,
  globe_tut                   TEXT,
  low_tax_topup_amount        INTEGER,
  utpr_mode                   TEXT,
  utpr_cit_rate               REAL,
  utpr_total_topup            INTEGER,
  utpr_art2_5_1_topup         INTEGER
);

-- 과세권 있는 관할국(QDMTT 등)과 차이 보고
CREATE TABLE jurisdiction_taxing_rights (
  group_id                    TEXT,
  jur_code                    TEXT,
  ord                         INTEGER,
  taxing_jur                  TEXT,
  diff_domestic_tut           TEXT,
  etr_difference              REAL,
  net_globe_difference        INTEGER,
  tut_difference              INTEGER
);

-- 어느 섹션을 어느 나라가 받는가 (RecJurCode)
CREATE TABLE section_recipient (
  group_id                    TEXT,
  section                     TEXT,
  section_key                 TEXT,
  ord                         INTEGER,
  recipient                   TEXT
);

-- ETR 계산 단위 = 관할국 × 소집단. 전체 합산치
CREATE TABLE etr (
  etr_id                      TEXT,
  group_id                    TEXT,
  jur_code                    TEXT,
  subgroup_type               TEXT,
  subgroup_entity_id          TEXT,
  fanil                       INTEGER,
  adjusted_fanil              INTEGER,
  net_globe_income            INTEGER,
  income_tax_expense          INTEGER,
  adjusted_covered_tax        INTEGER,
  aggregate_current_tax       INTEGER,
  defer_tax_adj_total         INTEGER,
  etr_rate                    REAL,
  topup_pct                   REAL,
  excess_profit               INTEGER,
  topup_tax                   INTEGER,
  sbie_payroll                INTEGER,
  sbie_tangible               INTEGER,
  safe_harbour                TEXT
);

-- ETR 수준 선택(Art3.2.2 등). XSD는 조항마다 블록을 따로 두지만 입력은 행으로
CREATE TABLE etr_election (
  etr_id                      TEXT,
  article                     TEXT,
  status                      INTEGER,
  election_year               TEXT,
  revocation_year             TEXT
);

-- CbCR 세이프하버용 연도별 재무자료 (1..3년)
CREATE TABLE financial_data (
  etr_id                      TEXT,
  ord                         INTEGER,
  year                        TEXT,
  revenue                     INTEGER,
  globe_revenue               INTEGER,
  net_globe_income            INTEGER,
  fanil                       INTEGER
);

-- 구성기업별 계산 = etr × entity
CREATE TABLE ce_computation (
  etr_id                      TEXT,
  entity_id                   TEXT,
  ord                         INTEGER,
  fanil                       INTEGER,
  adjusted_fanil              INTEGER,
  net_globe_income            INTEGER,
  income_tax                  INTEGER,
  adjusted_income_tax         INTEGER,
  adjusted_covered_tax        INTEGER,
  defer_tax_adj_total         INTEGER,
  defer_tax_expense           INTEGER,
  simpl_calculations          INTEGER,
  art_3_2_1                   INTEGER,
  tax_consol_group_entity_id  TEXT
);

-- CE 수준 선택 (Art1.5.3, 3.2.1b, 3.2.1c, 4.4.7, 4.5.6)
CREATE TABLE ce_election (
  etr_id                      TEXT,
  entity_id                   TEXT,
  article                     TEXT,
  status                      INTEGER,
  election_year               TEXT,
  revocation_year             TEXT
);

-- CE별 조정 항목. target이 NetGlobeIncome인지 AdjustedCoveredTax인지
CREATE TABLE ce_adjustment (
  etr_id                      TEXT,
  entity_id                   TEXT,
  target                      TEXT,
  ord                         INTEGER,
  item                        TEXT,
  amount                      INTEGER
);

-- 저율과세 구성기업과 IIR 배분
CREATE TABLE ltce (
  group_id                    TEXT,
  jur_code                    TEXT,
  entity_id                   TEXT,
  ord                         INTEGER
);

-- LTCE별 IIR 계산 (1..n)
CREATE TABLE ltce_iir (
  jur_code                    TEXT,
  entity_id                   TEXT,
  ord                         INTEGER,
  net_globe_income            INTEGER,
  topup_tax                   INTEGER
);

-- IIR을 적용하는 모기업별 배분
CREATE TABLE ltce_iir_parent (
  jur_code                    TEXT,
  entity_id                   TEXT,
  iir_ord                     INTEGER,
  ord                         INTEGER,
  parent_entity_id            TEXT,
  other_ownership_allocation  INTEGER,
  inclusion_ratio             REAL,
  topup_share                 INTEGER,
  iir_offset                  INTEGER,
  topup_tax                   INTEGER
);

-- UTPR 배분. 국가별 1행
CREATE TABLE utpr_attribution (
  group_id                    TEXT,
  ord                         INTEGER,
  country                     TEXT,
  carry_forward_in            INTEGER,
  employees                   INTEGER,
  tangible_asset_value        INTEGER,
  utpr_pct                    REAL,
  attributed                  INTEGER,
  add_cash_tax_expense        INTEGER,
  carry_forward_out           INTEGER
);

-- 섹션별 추가 데이터포인트
CREATE TABLE additional_data_point (
  group_id                    TEXT,
  section                     TEXT,
  section_key                 TEXT,
  ord                         INTEGER,
  description                 TEXT,
  amount                      INTEGER,
  percentage                  REAL,
  text                        TEXT,
  boolean                     INTEGER
);


INSERT INTO mne_group (group_id, name, upe_entity_id, cfs_of_upe, fas, currency, period_start, period_end) VALUES ('G1', 'Sora Materials Group', 'E1', 'GIR501', 'IFRS', 'USD', '2025-01-01', '2025-12-31');

INSERT INTO filing (filing_id, group_id, message_ref_id, transmitting_country, receiving_country, message_type_indic, reporting_period, sent_at, sending_entity_in, contact, filing_entity_id, filing_role, additional_info, unreported_change_corp_str, schema_version) VALUES ('F1', 'G1', 'KR2025SORA000001', 'KR', 'KR', 'GIR101', '2025-12-31', '2026-06-15T09:30:00', '1208812345', 'tax.reporting@sora-materials.example', 'E1', 'GIR401', NULL, 0, '1.0');

INSERT INTO entity (entity_id, group_id, name, main_country, is_upe, excluded_upe_status, art_10_3_5_country, is_non_material, pope_ipe, qiir_exception_rule, qiir_exception_entity_id, qutpr_art9_3, qutpr_agg_ownership, qutpr_upe_ownership, other_fas) VALUES ('E1', 'G1', 'Sora Materials Co., Ltd.', 'KR', 1, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO entity (entity_id, group_id, name, main_country, is_upe, excluded_upe_status, art_10_3_5_country, is_non_material, pope_ipe, qiir_exception_rule, qiir_exception_entity_id, qutpr_art9_3, qutpr_agg_ownership, qutpr_upe_ownership, other_fas) VALUES ('E2', 'G1', 'Sora Singapore Pte. Ltd.', 'SG', 0, NULL, NULL, 0, 'GIR902', NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO entity (entity_id, group_id, name, main_country, is_upe, excluded_upe_status, art_10_3_5_country, is_non_material, pope_ipe, qiir_exception_rule, qiir_exception_entity_id, qutpr_art9_3, qutpr_agg_ownership, qutpr_upe_ownership, other_fas) VALUES ('E3', 'G1', 'Sora Advanced Materials GmbH', 'DE', 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, 'German GAAP');
INSERT INTO entity (entity_id, group_id, name, main_country, is_upe, excluded_upe_status, art_10_3_5_country, is_non_material, pope_ipe, qiir_exception_rule, qiir_exception_entity_id, qutpr_art9_3, qutpr_agg_ownership, qutpr_upe_ownership, other_fas) VALUES ('E4', 'G1', 'Sora Vietnam Co., Ltd.', 'VN', 0, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO entity_tin (entity_id, ord, tin, issued_by, tin_type, unknown) VALUES ('E1', 1, '120-88-12345', 'KR', 'GIR3001', 0);
INSERT INTO entity_tin (entity_id, ord, tin, issued_by, tin_type, unknown) VALUES ('E2', 1, '201912345K', 'SG', 'GIR3001', 0);
INSERT INTO entity_tin (entity_id, ord, tin, issued_by, tin_type, unknown) VALUES ('E2', 2, 'T19SG0001A', 'SG', 'GIR3002', 0);
INSERT INTO entity_tin (entity_id, ord, tin, issued_by, tin_type, unknown) VALUES ('E3', 1, 'DE812345678', 'DE', 'GIR3001', 0);
INSERT INTO entity_tin (entity_id, ord, tin, issued_by, tin_type, unknown) VALUES ('E4', 1, '0312345678', 'VN', 'GIR3001', 0);

INSERT INTO entity_country (entity_id, ord, country) VALUES ('E1', 1, 'KR');
INSERT INTO entity_country (entity_id, ord, country) VALUES ('E2', 1, 'SG');
INSERT INTO entity_country (entity_id, ord, country) VALUES ('E3', 1, 'DE');
INSERT INTO entity_country (entity_id, ord, country) VALUES ('E4', 1, 'VN');

INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E1', 1, 'GIR202');
INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E1', 2, 'GIR204');
INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E2', 1, 'GIR201');
INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E2', 2, 'GIR204');
INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E3', 1, 'GIR204');
INSERT INTO entity_rule (entity_id, ord, rule) VALUES ('E4', 1, 'GIR205');

INSERT INTO entity_globe_status (entity_id, ord, status) VALUES ('E1', 1, 'GIR301');
INSERT INTO entity_globe_status (entity_id, ord, status) VALUES ('E2', 1, 'GIR301');
INSERT INTO entity_globe_status (entity_id, ord, status) VALUES ('E3', 1, 'GIR301');
INSERT INTO entity_globe_status (entity_id, ord, status) VALUES ('E4', 1, 'GIR315');

INSERT INTO ownership (owned_entity_id, ord, ownership_type, owner_entity_id, percentage) VALUES ('E2', 1, 'GIR801', 'E1', 1.0);
INSERT INTO ownership (owned_entity_id, ord, ownership_type, owner_entity_id, percentage) VALUES ('E3', 1, 'GIR802', 'E2', 0.7);
INSERT INTO ownership (owned_entity_id, ord, ownership_type, owner_entity_id, percentage) VALUES ('E3', 2, 'GIR806', NULL, 0.3);
INSERT INTO ownership (owned_entity_id, ord, ownership_type, owner_entity_id, percentage) VALUES ('E4', 1, 'GIR802', 'E2', 1.0);

INSERT INTO excluded_entity (group_id, ord, name, type, changed) VALUES ('G1', 1, 'Sora Employee Pension Fund', 'GIR1004', 0);

INSERT INTO jurisdiction (group_id, jur_code, local_currency, etr_range, sbie_not_applicable, sbie_no_tut, qdmtt_tut, globe_tut, low_tax_topup_amount, utpr_mode, utpr_cit_rate, utpr_total_topup, utpr_art2_5_1_topup) VALUES ('G1', 'KR', 'KRW', 'GIR1310', 1, 1, 'GIR1401', 'GIR1501', NULL, NULL, NULL, NULL, NULL);
INSERT INTO jurisdiction (group_id, jur_code, local_currency, etr_range, sbie_not_applicable, sbie_no_tut, qdmtt_tut, globe_tut, low_tax_topup_amount, utpr_mode, utpr_cit_rate, utpr_total_topup, utpr_art2_5_1_topup) VALUES ('G1', 'SG', 'SGD', 'GIR1304', 0, 0, 'GIR1402', 'GIR1502', 1350000, NULL, NULL, NULL, NULL);
INSERT INTO jurisdiction (group_id, jur_code, local_currency, etr_range, sbie_not_applicable, sbie_no_tut, qdmtt_tut, globe_tut, low_tax_topup_amount, utpr_mode, utpr_cit_rate, utpr_total_topup, utpr_art2_5_1_topup) VALUES ('G1', 'DE', 'EUR', 'GIR1312', 1, 1, 'GIR1401', 'GIR1501', NULL, NULL, NULL, NULL, NULL);
INSERT INTO jurisdiction (group_id, jur_code, local_currency, etr_range, sbie_not_applicable, sbie_no_tut, qdmtt_tut, globe_tut, low_tax_topup_amount, utpr_mode, utpr_cit_rate, utpr_total_topup, utpr_art2_5_1_topup) VALUES ('G1', 'VN', 'VND', 'GIR1314', 1, 1, 'GIR1401', 'GIR1501', NULL, NULL, NULL, NULL, NULL);

INSERT INTO jurisdiction_taxing_rights (group_id, jur_code, ord, taxing_jur, diff_domestic_tut, etr_difference, net_globe_difference, tut_difference) VALUES ('G1', 'SG', 1, 'SG', 'GIR1402', NULL, NULL, NULL);

INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'General', NULL, 1, 'KR');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'General', NULL, 2, 'SG');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'General', NULL, 3, 'DE');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Summary', 'KR', 1, 'KR');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Summary', 'SG', 1, 'SG');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Summary', 'DE', 1, 'DE');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Summary', 'VN', 1, 'VN');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Jurisdiction', 'KR', 1, 'KR');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Jurisdiction', 'SG', 1, 'SG');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Jurisdiction', 'SG', 2, 'KR');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Jurisdiction', 'DE', 1, 'DE');
INSERT INTO section_recipient (group_id, section, section_key, ord, recipient) VALUES ('G1', 'Jurisdiction', 'VN', 1, 'VN');

INSERT INTO etr (etr_id, group_id, jur_code, subgroup_type, subgroup_entity_id, fanil, adjusted_fanil, net_globe_income, income_tax_expense, adjusted_covered_tax, aggregate_current_tax, defer_tax_adj_total, etr_rate, topup_pct, excess_profit, topup_tax, sbie_payroll, sbie_tangible, safe_harbour) VALUES ('ETR_KR', 'G1', 'KR', 'GIR1601', NULL, 120000000, 120000000, 118500000, 28440000, 27900000, 28000000, -100000, 0.235443, 0.0, 0, 0, 30000000, 42000000, NULL);
INSERT INTO etr (etr_id, group_id, jur_code, subgroup_type, subgroup_entity_id, fanil, adjusted_fanil, net_globe_income, income_tax_expense, adjusted_covered_tax, aggregate_current_tax, defer_tax_adj_total, etr_rate, topup_pct, excess_profit, topup_tax, sbie_payroll, sbie_tangible, safe_harbour) VALUES ('ETR_SG', 'G1', 'SG', 'GIR1601', NULL, 45000000, 45000000, 44200000, 2650000, 2650000, 2700000, -50000, 0.059955, 0.090045, 15000000, 1350000, 9000000, 20200000, NULL);
INSERT INTO etr (etr_id, group_id, jur_code, subgroup_type, subgroup_entity_id, fanil, adjusted_fanil, net_globe_income, income_tax_expense, adjusted_covered_tax, aggregate_current_tax, defer_tax_adj_total, etr_rate, topup_pct, excess_profit, topup_tax, sbie_payroll, sbie_tangible, safe_harbour) VALUES ('ETR_DE', 'G1', 'DE', 'GIR1601', NULL, 38000000, 38000000, 37100000, 11130000, 10900000, 10800000, 100000, 0.293801, 0.0, 0, 0, 12500000, 18000000, NULL);
INSERT INTO etr (etr_id, group_id, jur_code, subgroup_type, subgroup_entity_id, fanil, adjusted_fanil, net_globe_income, income_tax_expense, adjusted_covered_tax, aggregate_current_tax, defer_tax_adj_total, etr_rate, topup_pct, excess_profit, topup_tax, sbie_payroll, sbie_tangible, safe_harbour) VALUES ('ETR_VN', 'G1', 'VN', 'GIR1607', NULL, 6000000, 6000000, 5900000, 600000, 600000, 600000, 0, 0.101695, 0.0, 0, 0, NULL, NULL, 'GIR1203');

INSERT INTO etr_election (etr_id, article, status, election_year, revocation_year) VALUES ('ETR_KR', 'Art3.2.8', 1, '2025-12-31', NULL);
INSERT INTO etr_election (etr_id, article, status, election_year, revocation_year) VALUES ('ETR_SG', 'Art3.2.5', 1, '2025-12-31', NULL);
INSERT INTO etr_election (etr_id, article, status, election_year, revocation_year) VALUES ('ETR_SG', 'NoDefTaxAllocation', 0, NULL, NULL);

INSERT INTO financial_data (etr_id, ord, year, revenue, globe_revenue, net_globe_income, fanil) VALUES ('ETR_VN', 1, '2025-12-31', 6400000, 6400000, 5900000, 6000000);
INSERT INTO financial_data (etr_id, ord, year, revenue, globe_revenue, net_globe_income, fanil) VALUES ('ETR_VN', 2, '2024-12-31', 6100000, 6100000, 5700000, 5800000);
INSERT INTO financial_data (etr_id, ord, year, revenue, globe_revenue, net_globe_income, fanil) VALUES ('ETR_VN', 3, '2023-12-31', 5900000, 5900000, 5400000, 5500000);

INSERT INTO ce_computation (etr_id, entity_id, ord, fanil, adjusted_fanil, net_globe_income, income_tax, adjusted_income_tax, adjusted_covered_tax, defer_tax_adj_total, defer_tax_expense, simpl_calculations, art_3_2_1, tax_consol_group_entity_id) VALUES ('ETR_KR', 'E1', 1, 120000000, 120000000, 118500000, 28440000, 28440000, 27900000, -100000, -100000, 0, 0, NULL);
INSERT INTO ce_computation (etr_id, entity_id, ord, fanil, adjusted_fanil, net_globe_income, income_tax, adjusted_income_tax, adjusted_covered_tax, defer_tax_adj_total, defer_tax_expense, simpl_calculations, art_3_2_1, tax_consol_group_entity_id) VALUES ('ETR_SG', 'E2', 1, 45000000, 45000000, 44200000, 2650000, 2650000, 2650000, -50000, -50000, 0, 1, NULL);
INSERT INTO ce_computation (etr_id, entity_id, ord, fanil, adjusted_fanil, net_globe_income, income_tax, adjusted_income_tax, adjusted_covered_tax, defer_tax_adj_total, defer_tax_expense, simpl_calculations, art_3_2_1, tax_consol_group_entity_id) VALUES ('ETR_DE', 'E3', 1, 38000000, 38000000, 37100000, 11130000, 11130000, 10900000, 100000, 100000, 0, 0, NULL);

INSERT INTO ce_election (etr_id, entity_id, article, status, election_year, revocation_year) VALUES ('ETR_SG', 'E2', 'Art3.2.1b', 1, '2025-12-31', NULL);
INSERT INTO ce_election (etr_id, entity_id, article, status, election_year, revocation_year) VALUES ('ETR_DE', 'E3', 'Art4.4.7', 1, '2024-12-31', NULL);

INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_KR', 'E1', 'NetGlobeIncome', 1, 'GIR2001', 28440000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_KR', 'E1', 'NetGlobeIncome', 2, 'GIR2002', -1500000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_SG', 'E2', 'NetGlobeIncome', 1, 'GIR2001', 2650000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_SG', 'E2', 'NetGlobeIncome', 2, 'GIR2007', -800000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_SG', 'E2', 'AdjustedCoveredTax', 1, 'GIR2101', -50000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_DE', 'E3', 'NetGlobeIncome', 1, 'GIR2001', 11130000);
INSERT INTO ce_adjustment (etr_id, entity_id, target, ord, item, amount) VALUES ('ETR_DE', 'E3', 'NetGlobeIncome', 2, 'GIR2006', -900000);

INSERT INTO ltce (group_id, jur_code, entity_id, ord) VALUES ('G1', 'SG', 'E2', 1);

INSERT INTO ltce_iir (jur_code, entity_id, ord, net_globe_income, topup_tax) VALUES ('SG', 'E2', 1, 44200000, 1350000);

INSERT INTO ltce_iir_parent (jur_code, entity_id, iir_ord, ord, parent_entity_id, other_ownership_allocation, inclusion_ratio, topup_share, iir_offset, topup_tax) VALUES ('SG', 'E2', 1, 1, 'E1', 0, 1.0, 1350000, 0, 1350000);


INSERT INTO additional_data_point (group_id, section, section_key, ord, description, amount, percentage, text, boolean) VALUES ('G1', 'Jurisdiction', 'SG', 1, 'Top-up tax computed under transitional rules; QDMTT not yet in force in SG for FY2025.', NULL, NULL, NULL, NULL);
