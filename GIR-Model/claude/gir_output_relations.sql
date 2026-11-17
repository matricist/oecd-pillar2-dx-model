-- GIR (GLOBEXML v1.0) output relations, generated from XSD
-- 모든 테이블: id = 이 요소 1건의 식별자(자유 형식 문자열), parent_id = 부모 테이블의 id, ord = 같은 부모 안 순번
-- NOT NULL = XSD minOccurs=1 (부모 그룹까지 전부 필수인 경우), CHECK = enum

CREATE TABLE GLOBE_OECD (
  id         VARCHAR(200) PRIMARY KEY
  , version                                            VARCHAR(10)
  , MessageSpec_SendingEntityIN                        VARCHAR(200)
  , MessageSpec_TransmittingCountry                    VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , MessageSpec_ReceivingCountry                       VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , MessageSpec_MessageType                            VARCHAR(3) NOT NULL CHECK (MessageSpec_MessageType IN ('GIR'))
  , MessageSpec_Warning                                VARCHAR(4000)
  , MessageSpec_Contact                                VARCHAR(4000)
  , MessageSpec_MessageRefId                           VARCHAR(170) NOT NULL
  , MessageSpec_MessageTypeIndic                       VARCHAR(6) NOT NULL CHECK (MessageSpec_MessageTypeIndic IN ('GIR101', 'GIR102', 'GIR103'))
  , MessageSpec_ReportingPeriod                        DATE NOT NULL
  , MessageSpec_Timestamp                              TIMESTAMP NOT NULL
);  -- /GLOBE_OECD  [1..1]

CREATE TABLE GLOBEBody (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBE_OECD(id)
  , ord        INTEGER NOT NULL
  , FilingInfo_FilingCE_ResCountryCode                 VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , FilingInfo_FilingCE_Name                           VARCHAR(200) NOT NULL
  , FilingInfo_FilingCE_TIN                            VARCHAR(200) NOT NULL
  , FilingInfo_FilingCE_TIN_issuedBy                   VARCHAR(2)  -- 251 enum values, see meta
  , FilingInfo_FilingCE_TIN_unknown                    BOOLEAN
  , FilingInfo_FilingCE_TIN_TypeOfTIN                  VARCHAR(7) CHECK (FilingInfo_FilingCE_TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , FilingInfo_FilingCE_Role                           VARCHAR(6) NOT NULL CHECK (FilingInfo_FilingCE_Role IN ('GIR401', 'GIR402', 'GIR403', 'GIR404', 'GIR405'))
  , FilingInfo_AccountingInfo_CFSofUPE                 VARCHAR(6) NOT NULL CHECK (FilingInfo_AccountingInfo_CFSofUPE IN ('GIR501', 'GIR502', 'GIR503', 'GIR504'))
  , FilingInfo_AccountingInfo_FAS                      VARCHAR(200) NOT NULL
  , FilingInfo_AccountingInfo_Currency                 VARCHAR(3) NOT NULL  -- 186 enum values, see meta
  , FilingInfo_Period_Start                            DATE NOT NULL
  , FilingInfo_Period_End                              DATE NOT NULL
  , FilingInfo_NameMNE                                 VARCHAR(200) NOT NULL
  , FilingInfo_AdditionalInfo                          VARCHAR(4000)
  , FilingInfo_DocSpec_DocTypeIndic                    VARCHAR(6) NOT NULL CHECK (FilingInfo_DocSpec_DocTypeIndic IN ('OECD0', 'OECD1', 'OECD2', 'OECD3', 'OECD10', 'OECD11', 'OECD12', 'OECD13'))
  , FilingInfo_DocSpec_DocRefId                        VARCHAR(200) NOT NULL
  , FilingInfo_DocSpec_CorrDocRefId                    VARCHAR(200)
  , GeneralSection_CorporateStructure_UnreportChangeCorpStr BOOLEAN
  , GeneralSection_DocSpec_DocTypeIndic                VARCHAR(6) CHECK (GeneralSection_DocSpec_DocTypeIndic IN ('OECD0', 'OECD1', 'OECD2', 'OECD3', 'OECD10', 'OECD11', 'OECD12', 'OECD13'))
  , GeneralSection_DocSpec_DocRefId                    VARCHAR(200)
  , GeneralSection_DocSpec_CorrDocRefId                VARCHAR(200)
);  -- /GLOBE_OECD/GLOBEBody  [1..n]

CREATE TABLE GeneralSection_RecJurCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/RecJurCode  [1..n]

CREATE TABLE UPE (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , choice                                             VARCHAR(11) NOT NULL CHECK (choice IN ('ExcludedUPE', 'OtherUPE'))
  , ExcludedUPE_ExcludedUPEStatus                      VARCHAR(6) CHECK (ExcludedUPE_ExcludedUPEStatus IN ('GIR601', 'GIR602', 'GIR603', 'GIR604', 'GIR605', 'GIR606'))
  , ExcludedUPE_Art10_3_5                              VARCHAR(2)  -- 251 enum values, see meta
  , ExcludedUPE_ID_Name                                VARCHAR(200)
  , OtherUPE_ID_Name                                   VARCHAR(200)
  , OtherUPE_Art10_3_5                                 VARCHAR(2)  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE  [1..n]

CREATE TABLE ExcludedUPE_ID_ResCountryCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/ExcludedUPE/ID/ResCountryCode  [0..n]

CREATE TABLE ExcludedUPE_ID_TIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/ExcludedUPE/ID/TIN  [1..n]

CREATE TABLE ExcludedUPE_ID_Rules (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR201', 'GIR202', 'GIR203', 'GIR204', 'GIR205'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/ExcludedUPE/ID/Rules  [0..n]

CREATE TABLE ExcludedUPE_ID_GlobeStatus (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR301', 'GIR302', 'GIR303', 'GIR304', 'GIR305', 'GIR306', 'GIR307', 'GIR308', 'GIR309', 'GIR310', 'GIR311', 'GIR312', 'GIR313', 'GIR314', 'GIR315', 'GIR316', 'GIR317', 'GIR318'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/ExcludedUPE/ID/GlobeStatus  [1..n]

CREATE TABLE OtherUPE_ID_ResCountryCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/OtherUPE/ID/ResCountryCode  [1..n]

CREATE TABLE OtherUPE_ID_TIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/OtherUPE/ID/TIN  [1..n]

CREATE TABLE OtherUPE_ID_Rules (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR201', 'GIR202', 'GIR203', 'GIR204', 'GIR205'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/OtherUPE/ID/Rules  [1..n]

CREATE TABLE OtherUPE_ID_GlobeStatus (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR301', 'GIR302', 'GIR303', 'GIR304', 'GIR305', 'GIR306', 'GIR307', 'GIR308', 'GIR309', 'GIR310', 'GIR311', 'GIR312', 'GIR313', 'GIR314', 'GIR315', 'GIR316', 'GIR317', 'GIR318'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/UPE/[C1]/OtherUPE/ID/GlobeStatus  [1..n]

CREATE TABLE CE (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , ID_Name                                            VARCHAR(200) NOT NULL
  , QIIR_POPE_IPE                                      VARCHAR(6) CHECK (QIIR_POPE_IPE IN ('GIR901', 'GIR902', 'GIR903'))
  , QIIR_Exception_ExceptionRule_choice                VARCHAR(8) CHECK (QIIR_Exception_ExceptionRule_choice IN ('Art2.1.3', 'Art2.1.5'))
  , QIIR_Exception_ExceptionRule_Art2_1_3              BOOLEAN
  , QIIR_Exception_ExceptionRule_Art2_1_5              BOOLEAN
  , QIIR_Exception_TIN                                 VARCHAR(200)
  , QIIR_Exception_TIN_issuedBy                        VARCHAR(2)  -- 251 enum values, see meta
  , QIIR_Exception_TIN_unknown                         BOOLEAN
  , QIIR_Exception_TIN_TypeOfTIN                       VARCHAR(7) CHECK (QIIR_Exception_TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , QUTPR_Art9_3                                       BOOLEAN
  , QUTPR_AggOwnership                                 DECIMAL(9,6)
  , QUTPR_UPEOwnership                                 BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE  [0..n]

CREATE TABLE CE_ID_ResCountryCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/ID/ResCountryCode  [1..n]

CREATE TABLE CE_ID_TIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/ID/TIN  [1..n]

CREATE TABLE CE_ID_Rules (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR201', 'GIR202', 'GIR203', 'GIR204', 'GIR205'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/ID/Rules  [1..n]

CREATE TABLE CE_ID_GlobeStatus (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR301', 'GIR302', 'GIR303', 'GIR304', 'GIR305', 'GIR306', 'GIR307', 'GIR308', 'GIR309', 'GIR310', 'GIR311', 'GIR312', 'GIR313', 'GIR314', 'GIR315', 'GIR316', 'GIR317', 'GIR318'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/ID/GlobeStatus  [1..n]

CREATE TABLE OwnershipChange (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , ChangeDate                                         DATE NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/OwnershipChange  [0..n]

CREATE TABLE PreGlobeStatus (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES OwnershipChange(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR701', 'GIR702', 'GIR703', 'GIR704', 'GIR705', 'GIR706', 'GIR707', 'GIR708', 'GIR709', 'GIR710', 'GIR711', 'GIR712', 'GIR713', 'GIR714', 'GIR715', 'GIR716', 'GIR717', 'GIR718', 'GIR719', 'GIR720', 'GIR721'))
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/OwnershipChange/PreGlobeStatus  [1..n]

CREATE TABLE PreOwnership (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES OwnershipChange(id)
  , ord        INTEGER NOT NULL
  , OwnershipType                                      VARCHAR(6) NOT NULL CHECK (OwnershipType IN ('GIR801', 'GIR802', 'GIR803', 'GIR804', 'GIR805', 'GIR806'))
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , PreOwnershipPercentage                             DECIMAL(9,6) NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/OwnershipChange/PreOwnership  [0..n]

CREATE TABLE Ownership (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CE(id)
  , ord        INTEGER NOT NULL
  , OwnershipType                                      VARCHAR(6) NOT NULL CHECK (OwnershipType IN ('GIR801', 'GIR802', 'GIR803', 'GIR804', 'GIR805', 'GIR806'))
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , OwnershipPercentage                                DECIMAL(9,6) NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/CE/Ownership  [1..n]

CREATE TABLE ExcludedEntity (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , Name                                               VARCHAR(200) NOT NULL
  , Type                                               VARCHAR(7) NOT NULL CHECK (Type IN ('GIR1001', 'GIR1002', 'GIR1003', 'GIR1004', 'GIR1005', 'GIR1006', 'GIR1007', 'GIR1008'))
  , Change                                             BOOLEAN NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/CorporateStructure/ExcludedEntity  [0..n]

CREATE TABLE GeneralSection_AdditionalDataPoint (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , Description                                        VARCHAR(170)
  , Amount                                             INTEGER
  , Percentage                                         DECIMAL(9,6)
  , Text                                               VARCHAR(4000)
  , Boolean                                            BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/GeneralSection/AdditionalDataPoint  [0..n]

CREATE TABLE Summary (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , Jurisdiction_JurisdictionName                      VARCHAR(2)  -- 251 enum values, see meta
  , ETRRange                                           VARCHAR(7) CHECK (ETRRange IN ('GIR1301', 'GIR1302', 'GIR1303', 'GIR1304', 'GIR1305', 'GIR1306', 'GIR1307', 'GIR1308', 'GIR1309', 'GIR1310', 'GIR1311', 'GIR1312', 'GIR1313', 'GIR1314'))
  , SBIE_NotApplicable                                 BOOLEAN
  , SBIE_NoTut                                         BOOLEAN
  , QDMTTut                                            VARCHAR(7) CHECK (QDMTTut IN ('GIR1401', 'GIR1402', 'GIR1403', 'GIR1404', 'GIR1405', 'GIR1406', 'GIR1407', 'GIR1408', 'GIR1409'))
  , GLoBETut                                           VARCHAR(7) CHECK (GLoBETut IN ('GIR1501', 'GIR1502', 'GIR1503', 'GIR1504', 'GIR1505', 'GIR1506', 'GIR1507', 'GIR1508', 'GIR1509'))
  , DocSpec_DocTypeIndic                               VARCHAR(6) NOT NULL CHECK (DocSpec_DocTypeIndic IN ('OECD0', 'OECD1', 'OECD2', 'OECD3', 'OECD10', 'OECD11', 'OECD12', 'OECD13'))
  , DocSpec_DocRefId                                   VARCHAR(200) NOT NULL
  , DocSpec_CorrDocRefId                               VARCHAR(200)
);  -- /GLOBE_OECD/GLOBEBody/Summary  [0..n]

CREATE TABLE Summary_RecJurCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Summary(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/Summary/RecJurCode  [1..n]

CREATE TABLE Jurisdiction_Subgroup (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Summary(id)
  , ord        INTEGER NOT NULL
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/Summary/Jurisdiction/Subgroup  [0..n]

CREATE TABLE Jurisdiction_Subgroup_TypeofSubGroup (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Jurisdiction_Subgroup(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR1101', 'GIR1102', 'GIR1103', 'GIR1104', 'GIR1105', 'GIR1106'))
);  -- /GLOBE_OECD/GLOBEBody/Summary/Jurisdiction/Subgroup/TypeofSubGroup  [1..n]

CREATE TABLE Summary_JurWithTaxingRights (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Summary(id)
  , ord        INTEGER NOT NULL
  , JurisdictionName                                   VARCHAR(2)  -- 251 enum values, see meta
  , DiffDomesticTut                                    VARCHAR(7) CHECK (DiffDomesticTut IN ('GIR1501', 'GIR1502', 'GIR1503', 'GIR1504', 'GIR1505', 'GIR1506', 'GIR1507', 'GIR1508', 'GIR1509'))
);  -- /GLOBE_OECD/GLOBEBody/Summary/JurWithTaxingRights  [0..n]

CREATE TABLE SafeHarbour (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Summary(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR1201', 'GIR1202', 'GIR1203', 'GIR1204', 'GIR1205', 'GIR1206', 'GIR1207', 'GIR1208', 'GIR1209'))
);  -- /GLOBE_OECD/GLOBEBody/Summary/SafeHarbour  [0..n]

CREATE TABLE Summary_AdditionalDataPoint (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Summary(id)
  , ord        INTEGER NOT NULL
  , Description                                        VARCHAR(170)
  , Amount                                             INTEGER
  , Percentage                                         DECIMAL(9,6)
  , Text                                               VARCHAR(4000)
  , Boolean                                            BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/Summary/AdditionalDataPoint  [0..n]

CREATE TABLE JurisdictionSection (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , Jurisdiction                                       VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , LocalCurrency                                      VARCHAR(3)  -- 186 enum values, see meta
  , GLoBETax_InitialIntActivity_StartDate              DATE
  , GLoBETax_InitialIntActivity_ReferenceJurisdiction_ResCountryCode VARCHAR(2)  -- 251 enum values, see meta
  , GLoBETax_InitialIntActivity_ReferenceJurisdiction_TangibleAssetValue INTEGER
  , GLoBETax_InitialIntActivity_RFYNumberOfJurisdictions INTEGER
  , GLoBETax_InitialIntActivity_RFYSumTangibleAssetValue INTEGER
  , LowTaxJurisdiction_TopUpTaxAmount                  INTEGER
  , LowTaxJurisdiction_UTPR_choice                     VARCHAR(15) CHECK (LowTaxJurisdiction_UTPR_choice IN ('UTPRSafeHarbour', 'UTPRCalculation'))
  , LowTaxJurisdiction_UTPR_UTPRSafeHarbour_CITRate    DECIMAL(9,6)
  , LowTaxJurisdiction_UTPR_UTPRCalculation_TotalUTPRTopUpTax INTEGER
  , LowTaxJurisdiction_UTPR_UTPRCalculation_Article2_5_1TopUpTax INTEGER
  , DocSpec_DocTypeIndic                               VARCHAR(6) NOT NULL CHECK (DocSpec_DocTypeIndic IN ('OECD0', 'OECD1', 'OECD2', 'OECD3', 'OECD10', 'OECD11', 'OECD12', 'OECD13'))
  , DocSpec_DocRefId                                   VARCHAR(200) NOT NULL
  , DocSpec_CorrDocRefId                               VARCHAR(200)
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection  [0..n]

CREATE TABLE JurisdictionSection_RecJurCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/RecJurCode  [1..n]

CREATE TABLE JurisdictionSection_JurWithTaxingRights (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , JurisdictionName                                   VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , ReportDifference_ETRDifference                     DECIMAL(9,6)
  , ReportDifference_AdjCoveredTaxDifference_AggCurrentTaxExpense INTEGER
  , ReportDifference_AdjCoveredTaxDifference_QRTCExpense INTEGER
  , ReportDifference_AdjCoveredTaxDifference_OtherTaxCredits INTEGER
  , ReportDifference_AdjCoveredTaxDifference_DeferTaxExpense INTEGER
  , ReportDifference_NetGLoBEDifference                INTEGER
  , ReportDifference_SBIEDifference                    INTEGER
  , ReportDifference_AddCurrentTuTDifference           INTEGER
  , ReportDifference_TuTDifference                     INTEGER
  , ReportDifference_ElectionsDifference               VARCHAR(4000)
  , ReportDifference_QRTCIncome                        INTEGER
  , ReportDifference_ExcessNegTaxCarryForw             INTEGER
  , ReportDifference_TransitionDifference              BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/JurWithTaxingRights  [0..n]

CREATE TABLE JurisdictionSection_JurWithTaxingRights_Subgroup (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection_JurWithTaxingRights(id)
  , ord        INTEGER NOT NULL
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/JurWithTaxingRights/Subgroup  [0..n]

CREATE TABLE JurWithTaxingRights_Subgroup_TypeofSubGroup (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection_JurWithTaxingRights_Subgroup(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR1101', 'GIR1102', 'GIR1103', 'GIR1104', 'GIR1105', 'GIR1106'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/JurWithTaxingRights/Subgroup/TypeofSubGroup  [1..n]

CREATE TABLE ETR (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , SubGroup_TIN                                       VARCHAR(200)
  , SubGroup_TIN_issuedBy                              VARCHAR(2)  -- 251 enum values, see meta
  , SubGroup_TIN_unknown                               BOOLEAN
  , SubGroup_TIN_TypeOfTIN                             VARCHAR(7) CHECK (SubGroup_TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Basis VARCHAR(7) CHECK (ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Basis IN ('GIR2901', 'GIR2902'))
  , ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Average_Revenue INTEGER
  , ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Average_GlobeRevenue INTEGER
  , ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Average_NetGlobeIncome INTEGER
  , ETRStatus_ETRException_Deminimis_SimplifiedNMCECalc_Average_FANIL INTEGER
  , ETRStatus_ETRException_TransitionalCbCRSafeHarbour_Revenue INTEGER
  , ETRStatus_ETRException_TransitionalCbCRSafeHarbour_Profit INTEGER
  , ETRStatus_ETRException_TransitionalCbCRSafeHarbour_IncomeTax INTEGER
  , ETRStatus_ETRException_UTPRSafeHarbour_CITRate     DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_FANIL  INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedFANIL INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_IntShippingIncome_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_IntShippingIncome_TotalIntShipIncome INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_IntShippingIncome_FiftyPercentCap INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_IntShippingIncome_TotalQualifiedAncIncome INTEGER
  , ETRStatus_ETRComputation_OverallComputation_NetGlobeIncome_IntShippingIncome_ExcessOfCap INTEGER
  , ETRStatus_ETRComputation_OverallComputation_IncomeTaxExpense INTEGER
  , ETRStatus_ETRComputation_OverallComputation_ETRRate DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_TopUpTaxPercentage DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_AggregrateCurrentTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_PostFilingAdjust_DeferTaxAsset_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_PostFilingAdjust_CoveredTaxRefund_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeemedDistTax_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeemedDistTax_Election_Reduction INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeemedDistTax_Election_IncrementalTopUpTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeemedDistTax_Election_Ratio DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_DefTaxAmt INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_DiffCarryValue INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_GLoBEValue INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_BefRecastAdjust INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_TotalAdjust INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_PreRecast INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_Recast_Higher INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_DeferTaxAdjustAmt_Recast_Lower INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdjustedCoveredTax_TransBlendCFC_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_SubstanceExclusion_Total INTEGER
  , ETRStatus_ETRComputation_OverallComputation_SubstanceExclusion_PayrollCost INTEGER
  , ETRStatus_ETRComputation_OverallComputation_SubstanceExclusion_PayrollMarkUp DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_SubstanceExclusion_TangibleAssetValue INTEGER
  , ETRStatus_ETRComputation_OverallComputation_SubstanceExclusion_TangibleAssetMarkup DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_ExcessProfits INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdditionalTopUpTax_Art4_1_5_AdjustedCoveredTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdditionalTopUpTax_Art4_1_5_GlobeLoss INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdditionalTopUpTax_Art4_1_5_ExpectedAdjustedCoveredTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_AdditionalTopUpTax_Art4_1_5_AdditionalTopUpTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_FAS VARCHAR(200)
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_Amount INTEGER
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_MinRate DECIMAL(9,6)
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_BasisforBlending VARCHAR(4000)
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_SBIEAvailable BOOLEAN
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_DeMinAvailable BOOLEAN
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_Currency VARCHAR(3)  -- 186 enum values, see meta
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_CurrencyElection_Status BOOLEAN
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_CurrencyElection_ElectionYear DATE
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_CurrencyElection_RevocationYear DATE
  , ETRStatus_ETRComputation_OverallComputation_QDMTT_CurrencyElection_Currency VARCHAR(7) CHECK (ETRStatus_ETRComputation_OverallComputation_QDMTT_CurrencyElection_Currency IN ('GIR3101', 'GIR3102'))
  , ETRStatus_ETRComputation_OverallComputation_TopUpTax INTEGER
  , ETRStatus_ETRComputation_OverallComputation_ExcessNegTaxExpense_PriorYearBalance INTEGER
  , ETRStatus_ETRComputation_OverallComputation_ExcessNegTaxExpense_GeneratedInRFY INTEGER
  , ETRStatus_ETRComputation_OverallComputation_ExcessNegTaxExpense_UtilizedInRFY INTEGER
  , ETRStatus_ETRComputation_OverallComputation_ExcessNegTaxExpense_Remaining INTEGER
  , Election_Art3_2_6                                  BOOLEAN
  , Election_Art4_1_5                                  BOOLEAN
  , Election_Art4_6_1                                  BOOLEAN
  , Election_Art5_3_1                                  BOOLEAN
  , Election_Art3_2_2_Status                           BOOLEAN
  , Election_Art3_2_2_ElectionYear                     DATE
  , Election_Art3_2_2_RevocationYear                   DATE
  , Election_Art3_2_5_Status                           BOOLEAN
  , Election_Art3_2_5_ElectionYear                     DATE
  , Election_Art3_2_5_RevocationYear                   DATE
  , Election_Art3_2_8_Status                           BOOLEAN
  , Election_Art3_2_8_ElectionYear                     DATE
  , Election_Art3_2_8_RevocationYear                   DATE
  , Election_NoDefTaxAllocation_Status                 BOOLEAN
  , Election_NoDefTaxAllocation_ElectionYear           DATE
  , Election_NoDefTaxAllocation_RevocationYear         DATE
  , Election_Art4_5_Status                             BOOLEAN
  , Election_Art4_5_ElectionYear                       DATE
  , Election_Art4_5_RevocationYear                     DATE
  , Election_Art3_2_1_c_Status                         BOOLEAN
  , Election_Art3_2_1_c_ElectionYear                   DATE
  , Election_Art3_2_1_c_RevocationYear                 DATE
  , Election_Art3_2_1_c_QualOwnerIntentBalance         INTEGER
  , Election_Art3_2_1_c_Additions                      INTEGER
  , Election_Art3_2_1_c_Reductions                     INTEGER
  , Election_Art3_2_1_c_OutstandingBalance             INTEGER
  , Election_SimplifiedReporting                       BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR  [0..n]

CREATE TABLE SubGroup_TypeofSubGroup (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR1601', 'GIR1602', 'GIR1603', 'GIR1604', 'GIR1605', 'GIR1606', 'GIR1607', 'GIR1608', 'GIR1609'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/SubGroup/TypeofSubGroup  [1..n]

CREATE TABLE FinancialData (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , Revenue                                            INTEGER
  , GlobeRevenue                                       INTEGER NOT NULL
  , NetGlobeIncome                                     INTEGER NOT NULL
  , FANIL                                              INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRException/Deminimis-SimplifiedNMCECalc/FinancialData  [1..3]

CREATE TABLE CEComputation (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , AdjustedFANIL_Total                                INTEGER NOT NULL
  , AdjustedFANIL_FANIL                                INTEGER NOT NULL
  , NetGlobeIncome_Total                               INTEGER NOT NULL
  , NetGlobeIncome_IntShippingIncome_InternationalShipIncome_Total INTEGER
  , NetGlobeIncome_IntShippingIncome_InternationalShipIncome_Revenue INTEGER
  , NetGlobeIncome_IntShippingIncome_InternationalShipIncome_Costs INTEGER
  , NetGlobeIncome_IntShippingIncome_QualifiedAncShipIncome_Total INTEGER
  , NetGlobeIncome_IntShippingIncome_QualifiedAncShipIncome_Category VARCHAR(7) CHECK (NetGlobeIncome_IntShippingIncome_QualifiedAncShipIncome_Category IN ('GIR2201', 'GIR2202', 'GIR2203', 'GIR2204', 'GIR2205'))
  , NetGlobeIncome_IntShippingIncome_QualifiedAncShipIncome_Revenue INTEGER
  , NetGlobeIncome_IntShippingIncome_QualifiedAncShipIncome_Costs INTEGER
  , NetGlobeIncome_IntShippingIncome_SubstanceExclusion_PayrollCosts INTEGER
  , NetGlobeIncome_IntShippingIncome_SubstanceExclusion_TangibleAssets INTEGER
  , NetGlobeIncome_IntShippingIncome_CoveredTaxes      INTEGER
  , AdjustedIncomeTax_Total                            INTEGER NOT NULL
  , AdjustedIncomeTax_IncomeTax                        INTEGER NOT NULL
  , AdjustedCoveredTax_Total                           INTEGER NOT NULL
  , AdjustedCoveredTax_DeferTaxAdjustAmt_Total         INTEGER NOT NULL
  , AdjustedCoveredTax_DeferTaxAdjustAmt_DeferTaxExpense INTEGER NOT NULL
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , Elections_Art1_5_3_Status                          BOOLEAN
  , Elections_Art1_5_3_ElectionYear                    DATE
  , Elections_Art1_5_3_RevocationYear                  DATE
  , Elections_SimplCalculations                        BOOLEAN
  , Elections_Art3_2_1                                 BOOLEAN
  , Elections_Art3_2_1b_Status                         BOOLEAN
  , Elections_Art3_2_1b_ElectionYear                   DATE
  , Elections_Art3_2_1b_RevocationYear                 DATE
  , Elections_Art3_2_1c_Status                         BOOLEAN
  , Elections_Art3_2_1c_ElectionYear                   DATE
  , Elections_Art3_2_1c_RevocationYear                 DATE
  , Elections_AggregatedReporting_TaxConsolGroupTIN    VARCHAR(200)
  , Elections_AggregatedReporting_TaxConsolGroupTIN_issuedBy VARCHAR(2)  -- 251 enum values, see meta
  , Elections_AggregatedReporting_TaxConsolGroupTIN_unknown BOOLEAN
  , Elections_AggregatedReporting_TaxConsolGroupTIN_TypeOfTIN VARCHAR(7) CHECK (Elections_AggregatedReporting_TaxConsolGroupTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , Elections_Art4_4_7_Status                          BOOLEAN
  , Elections_Art4_4_7_ElectionYear                    DATE
  , Elections_Art4_4_7_RevocationYear                  DATE
  , Elections_Art4_5_6_Status                          BOOLEAN
  , Elections_Art4_5_6_ElectionYear                    DATE
  , Elections_Art4_5_6_RevocationYear                  DATE
  , OtherFAS                                           VARCHAR(200)
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation  [0..n]

CREATE TABLE MainEntityPEandFTE (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , Basis                                              VARCHAR(7) NOT NULL CHECK (Basis IN ('GIR1701', 'GIR1702', 'GIR1703', 'GIR1704'))
  , OtherTIN                                           VARCHAR(200) NOT NULL
  , OtherTIN_issuedBy                                  VARCHAR(2)  -- 251 enum values, see meta
  , OtherTIN_unknown                                   BOOLEAN
  , OtherTIN_TypeOfTIN                                 VARCHAR(7) CHECK (OtherTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , ResCountryCode                                     VARCHAR(2)  -- 251 enum values, see meta
  , Additions                                          INTEGER NOT NULL
  , Reductions                                         INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedFANIL/Adjustment/MainEntityPEandFTE  [0..n]

CREATE TABLE CrossBorderAdjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , Basis                                              VARCHAR(7) NOT NULL CHECK (Basis IN ('GIR1801', 'GIR1802'))
  , OtherTIN                                           VARCHAR(200) NOT NULL
  , OtherTIN_issuedBy                                  VARCHAR(2)  -- 251 enum values, see meta
  , OtherTIN_unknown                                   BOOLEAN
  , OtherTIN_TypeOfTIN                                 VARCHAR(7) CHECK (OtherTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , ResCountryCode                                     VARCHAR(2)  -- 251 enum values, see meta
  , Additions                                          INTEGER
  , Reductions                                         INTEGER
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedFANIL/Adjustment/CrossBorderAdjustments  [0..n]

CREATE TABLE UPEAdjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , Basis                                              VARCHAR(7) NOT NULL CHECK (Basis IN ('GIR1901', 'GIR1902', 'GIR1903', 'GIR1904', 'GIR1905', 'GIR1906', 'GIR1907', 'GIR1908', 'GIR1909', 'GIR1910'))
  , Reductions_choice                                  VARCHAR(9) CHECK (Reductions_choice IN ('Amount', 'Exception'))
  , Reductions_Amount                                  INTEGER
  , Reductions_Exception                               BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedFANIL/Adjustment/UPEAdjustments  [0..n]

CREATE TABLE IdentificationOfOwners (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UPEAdjustments(id)
  , ord        INTEGER NOT NULL
  , OwnershipPercentage                                DECIMAL(9,6) NOT NULL
  , choice                                             VARCHAR(11) NOT NULL CHECK (choice IN ('IndOwners', 'EntityOwner'))
  , IndOwners_NumOfOwners                              INTEGER
  , IndOwners_ResCountryCode                           VARCHAR(2)  -- 251 enum values, see meta
  , IndOwners_TaxRate                                  DECIMAL(9,6)
  , EntityOwner_TIN                                    VARCHAR(200)
  , EntityOwner_TIN_issuedBy                           VARCHAR(2)  -- 251 enum values, see meta
  , EntityOwner_TIN_unknown                            BOOLEAN
  , EntityOwner_TIN_TypeOfTIN                          VARCHAR(7) CHECK (EntityOwner_TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , EntityOwner_ResCountryCode                         VARCHAR(2)  -- 251 enum values, see meta
  , EntityOwner_TaxRate                                DECIMAL(9,6)
  , EntityOwner_ExTypeOfEntity                         VARCHAR(7) CHECK (EntityOwner_ExTypeOfEntity IN ('GIR2801', 'GIR2802', 'GIR2803', 'GIR2804', 'GIR2805'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedFANIL/Adjustment/UPEAdjustments/IdentificationOfOwners  [1..n]

CREATE TABLE CEComputation_NetGlobeIncome_Adjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2001', 'GIR2002', 'GIR2003', 'GIR2004', 'GIR2005', 'GIR2006', 'GIR2007', 'GIR2008', 'GIR2009', 'GIR2010', 'GIR2011', 'GIR2012', 'GIR2013', 'GIR2014', 'GIR2015', 'GIR2016', 'GIR2017', 'GIR2018', 'GIR2019', 'GIR2020', 'GIR2021', 'GIR2022', 'GIR2023', 'GIR2024', 'GIR2025', 'GIR2026'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/NetGlobeIncome/Adjustments  [0..n]

CREATE TABLE NetGlobeIncome_Adjustments_Amount (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation_NetGlobeIncome_Adjustments(id)
  , ord        INTEGER NOT NULL
  , value                                              INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/NetGlobeIncome/Adjustments/Amount  [1..2]

CREATE TABLE Category (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR2101', 'GIR2102', 'GIR2103', 'GIR2104', 'GIR2105', 'GIR2106'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/NetGlobeIncome/IntShippingIncome/InternationalShipIncome/Category  [1..n]

CREATE TABLE CrossAllocation (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , OtherTIN                                           VARCHAR(200) NOT NULL
  , OtherTIN_issuedBy                                  VARCHAR(2)  -- 251 enum values, see meta
  , OtherTIN_unknown                                   BOOLEAN
  , OtherTIN_TypeOfTIN                                 VARCHAR(7) CHECK (OtherTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , ResCountryCode                                     VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , Additions                                          INTEGER
  , Reductions                                         INTEGER
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedIncomeTax/CrossAllocation  [0..n]

CREATE TABLE Basis (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CrossAllocation(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR2301', 'GIR2302', 'GIR2303', 'GIR2304', 'GIR2305', 'GIR2306', 'GIR2307', 'GIR2308', 'GIR2309'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedIncomeTax/CrossAllocation/Basis  [1..n]

CREATE TABLE CEComputation_AdjustedCoveredTax_Adjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2401', 'GIR2402', 'GIR2403', 'GIR2404', 'GIR2405', 'GIR2406', 'GIR2407', 'GIR2408', 'GIR2409', 'GIR2410', 'GIR2411', 'GIR2412', 'GIR2413', 'GIR2414', 'GIR2415', 'GIR2416', 'GIR2417'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedCoveredTax/Adjustments  [0..n]

CREATE TABLE AdjustedCoveredTax_Adjustments_Amount (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation_AdjustedCoveredTax_Adjustments(id)
  , ord        INTEGER NOT NULL
  , value                                              INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedCoveredTax/Adjustments/Amount  [1..2]

CREATE TABLE Adjustment (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2501', 'GIR2502', 'GIR2503', 'GIR2504', 'GIR2505', 'GIR2506', 'GIR2507', 'GIR2508', 'GIR2509', 'GIR2510', 'GIR2511', 'GIR2512', 'GIR2513', 'GIR2514', 'GIR2515', 'GIR2516'))
  , Recast_Higher                                      INTEGER
  , Recast_Lower                                       INTEGER
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedCoveredTax/DeferTaxAdjustAmt/Adjustment  [0..n]

CREATE TABLE Adjustment_Amount (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Adjustment(id)
  , ord        INTEGER NOT NULL
  , value                                              INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/AdjustedCoveredTax/DeferTaxAdjustAmt/Adjustment/Amount  [1..2]

CREATE TABLE Art6_3_4 (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , FYTriggerEvent                                     DATE NOT NULL
  , Inclusion_choice                                   VARCHAR(13) NOT NULL CHECK (Inclusion_choice IN ('Art6.3.4.c.i', 'Art6.3.4.c.ii'))
  , Inclusion_Art6_3_4_c_i                             BOOLEAN
  , Inclusion_Art6_3_4_c_ii                            BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/Elections/Art6.3.4  [0..n]

CREATE TABLE EntityTIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/Elections/AggregatedReporting/EntityTIN  [1..n]

CREATE TABLE Art7_5 (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , Status                                             BOOLEAN NOT NULL
  , ElectionYear                                       DATE NOT NULL
  , RevocationYear                                     DATE
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/Elections/Art7.5  [0..n]

CREATE TABLE CEOwnerTIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Art7_5(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/Elections/Art7.5/CEOwnerTIN  [1..n]

CREATE TABLE Art7_6 (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES CEComputation(id)
  , ord        INTEGER NOT NULL
  , Status                                             BOOLEAN NOT NULL
  , ElectionYear                                       DATE NOT NULL
  , RevocationYear                                     DATE
  , ActualDeemedDist                                   INTEGER NOT NULL
  , LocalCreditableTaxGross                            INTEGER NOT NULL
  , ShareOfUndistNetGlobeInc                           DECIMAL(9,6) NOT NULL
  , InvestmentEntityTIN                                VARCHAR(200) NOT NULL
  , InvestmentEntityTIN_issuedBy                       VARCHAR(2)  -- 251 enum values, see meta
  , InvestmentEntityTIN_unknown                        BOOLEAN
  , InvestmentEntityTIN_TypeOfTIN                      VARCHAR(7) CHECK (InvestmentEntityTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/CEComputation/Elections/Art7.6  [0..n]

CREATE TABLE OverallComputation_NetGlobeIncome_Adjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Amount                                             INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2001', 'GIR2002', 'GIR2003', 'GIR2004', 'GIR2005', 'GIR2006', 'GIR2007', 'GIR2008', 'GIR2009', 'GIR2010', 'GIR2011', 'GIR2012', 'GIR2013', 'GIR2014', 'GIR2015', 'GIR2016', 'GIR2017', 'GIR2018', 'GIR2019', 'GIR2020', 'GIR2021', 'GIR2022', 'GIR2023', 'GIR2024', 'GIR2025', 'GIR2026'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/NetGlobeIncome/Adjustments  [0..n]

CREATE TABLE OverallComputation_AdjustedCoveredTax_Adjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Amount                                             INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2701', 'GIR2702', 'GIR2703', 'GIR2704', 'GIR2705', 'GIR2706', 'GIR2707', 'GIR2708', 'GIR2709', 'GIR2710', 'GIR2711', 'GIR2712', 'GIR2713', 'GIR2714', 'GIR2715', 'GIR2716', 'GIR2717', 'GIR2718', 'GIR2719', 'GIR2720'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/Adjustments  [0..n]

CREATE TABLE DeferTaxAsset_AmountAttributed (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , Amount                                             INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/PostFilingAdjust/DeferTaxAsset/AmountAttributed  [0..n]

CREATE TABLE CoveredTaxRefund_AmountAttributed (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , Amount                                             INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/PostFilingAdjust/CoveredTaxRefund/AmountAttributed  [0..n]

CREATE TABLE Recapture (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , StartAmount                                        INTEGER NOT NULL
  , DDTYear_0                                          INTEGER NOT NULL
  , DDTYear_1                                          INTEGER NOT NULL
  , DDTYear_2                                          INTEGER NOT NULL
  , DDTYear_3                                          INTEGER NOT NULL
  , TotalDDT                                           INTEGER NOT NULL
  , EndAmount                                          INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/DeemedDistTax/Election/Recapture  [1..n]

CREATE TABLE DeferTaxAdjustAmt_Adjustments (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Amount                                             INTEGER NOT NULL
  , AdjustmentItem                                     VARCHAR(7) NOT NULL CHECK (AdjustmentItem IN ('GIR2501', 'GIR2502', 'GIR2503', 'GIR2504', 'GIR2505', 'GIR2506', 'GIR2507', 'GIR2508', 'GIR2509', 'GIR2510', 'GIR2511', 'GIR2512', 'GIR2513', 'GIR2514', 'GIR2515', 'GIR2516'))
  , RecaptureDeferred_DTLRFYMinus5                     INTEGER NOT NULL
  , RecaptureDeferred_RecapDTLRFYMinus5                INTEGER NOT NULL
  , RecaptureDeferred_DTLRFY                           INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_ReportingFiscalYear_AmountPreTransition INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_ReportingFiscalYear_AmountOutBalance INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_ReportingFiscalYear_AmountUnjustified INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_PriorFiscalYear_AmountPreTransition INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_PriorFiscalYear_AmountOutBalance INTEGER NOT NULL
  , RecaptureDeferred_AggregateDTL_PriorFiscalYear_AmountUnjustified INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/DeferTaxAdjustAmt/Adjustments  [0..n]

CREATE TABLE Transition (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , DeferredTaxLiabilityStart                          INTEGER
  , DeferredTaxLiabilityRecast                         INTEGER
  , DeferredTaxAssets_Total                            INTEGER
  , DeferredTaxAssets_DeferredTaxAssetStart            INTEGER
  , DeferredTaxAssets_DeferredTaxAssetRecast           INTEGER
  , DeferredTaxAssets_DeferredTaxAssetExcluded         INTEGER
  , Disposal_ResCountryCode                            VARCHAR(2)  -- 251 enum values, see meta
  , Disposal_NetDTADTL                                 INTEGER
  , Disposal_CarryingValue                             INTEGER
  , Disposal_TaxPaid                                   INTEGER
  , Disposal_DTADTL                                    INTEGER
  , AltJurisdiction                                    VARCHAR(2)  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/DeferTaxAdjustAmt/Transition  [0..n]

CREATE TABLE CFCJur (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Jurisdiction                                       VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , Allocation_SubGroupTIN                             VARCHAR(200) NOT NULL
  , Allocation_SubGroupTIN_issuedBy                    VARCHAR(2)  -- 251 enum values, see meta
  , Allocation_SubGroupTIN_unknown                     BOOLEAN
  , Allocation_SubGroupTIN_TypeOfTIN                   VARCHAR(7) CHECK (Allocation_SubGroupTIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , Allocation_AggAllocTax                             INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdjustedCoveredTax/TransBlendCFC/CFCJur  [1..n]

CREATE TABLE PEAllocation (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , JurOfOwners_choice                                 VARCHAR(14) NOT NULL CHECK (JurOfOwners_choice IN ('ResCountryCode', 'UPE', 'NotApplicable'))
  , JurOfOwners_ResCountryCode                         VARCHAR(2)  -- 251 enum values, see meta
  , JurOfOwners_UPE                                    BOOLEAN
  , JurOfOwners_NotApplicable                          BOOLEAN
  , PayrollCost_Total                                  INTEGER NOT NULL
  , PayrollCost_Allocation                             INTEGER NOT NULL
  , TangibleAssetValue_Total                           INTEGER NOT NULL
  , TangibleAssetValue_Allocation                      INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/SubstanceExclusion/PEAllocation  [0..n]

CREATE TABLE FTEAllocation (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , JurOfOwners_choice                                 VARCHAR(14) NOT NULL CHECK (JurOfOwners_choice IN ('ResCountryCode', 'UPE', 'NotApplicable'))
  , JurOfOwners_ResCountryCode                         VARCHAR(2)  -- 251 enum values, see meta
  , JurOfOwners_UPE                                    BOOLEAN
  , JurOfOwners_NotApplicable                          BOOLEAN
  , PayrollCost_Total                                  INTEGER NOT NULL
  , PayrollCost_Allocation                             INTEGER NOT NULL
  , TangibleAssetValue_Total                           INTEGER NOT NULL
  , TangibleAssetValue_Allocation                      INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/SubstanceExclusion/FTEAllocation  [0..n]

CREATE TABLE NONArt4_1_5 (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , Year                                               DATE NOT NULL
  , Previous_NetGlobeIncome                            INTEGER NOT NULL
  , Previous_AdjustedCoveredTax                        INTEGER NOT NULL
  , Previous_ETRRate                                   DECIMAL(9,6) NOT NULL
  , Previous_ExcessProfits                             INTEGER NOT NULL
  , Previous_TopUpTaxPercentage                        DECIMAL(9,6) NOT NULL
  , Previous_TopUpTax                                  INTEGER NOT NULL
  , Recalculated_NetGlobeIncome                        INTEGER NOT NULL
  , Recalculated_AdjustedCoveredTax                    INTEGER NOT NULL
  , Recalculated_ETRRate                               DECIMAL(9,6) NOT NULL
  , Recalculated_ExcessProfits                         INTEGER NOT NULL
  , Recalculated_TopUpTaxPercentage                    DECIMAL(9,6) NOT NULL
  , Recalculated_TopUpTax                              INTEGER NOT NULL
  , AdditionalTopUpTax                                 INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdditionalTopUpTax/NONArt4.1.5  [0..n]

CREATE TABLE Articles (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES NONArt4_1_5(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(7) NOT NULL CHECK (value IN ('GIR2601', 'GIR2602', 'GIR2603', 'GIR2604', 'GIR2605', 'GIR2606'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/OverallComputation/AdditionalTopUpTax/NONArt4.1.5/Articles  [1..n]

CREATE TABLE Non_MaterialCE (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES ETR(id)
  , ord        INTEGER NOT NULL
  , RFY_TotalRevenue                                   INTEGER NOT NULL
  , RFY_AggregateSimplified                            INTEGER
  , RFY_1_TotalRevenue                                 INTEGER
  , RFY_2_TotalRevenue                                 INTEGER
  , Average_TotalRevenue                               INTEGER NOT NULL
  , ID_Name                                            VARCHAR(200) NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/Non-MaterialCE  [0..n]

CREATE TABLE Non_MaterialCE_ID_ResCountryCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Non_MaterialCE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/Non-MaterialCE/ID/ResCountryCode  [1..n]

CREATE TABLE Non_MaterialCE_ID_TIN (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Non_MaterialCE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(200) NOT NULL
  , value_issuedBy                                     VARCHAR(2)  -- 251 enum values, see meta
  , value_unknown                                      BOOLEAN
  , value_TypeOfTIN                                    VARCHAR(7) CHECK (value_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/Non-MaterialCE/ID/TIN  [1..n]

CREATE TABLE Non_MaterialCE_ID_Rules (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Non_MaterialCE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR201', 'GIR202', 'GIR203', 'GIR204', 'GIR205'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/Non-MaterialCE/ID/Rules  [1..n]

CREATE TABLE Non_MaterialCE_ID_GlobeStatus (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES Non_MaterialCE(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(6) NOT NULL CHECK (value IN ('GIR301', 'GIR302', 'GIR303', 'GIR304', 'GIR305', 'GIR306', 'GIR307', 'GIR308', 'GIR309', 'GIR310', 'GIR311', 'GIR312', 'GIR313', 'GIR314', 'GIR315', 'GIR316', 'GIR317', 'GIR318'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/ETR/ETRStatus/ETRComputation/Non-MaterialCE/ID/GlobeStatus  [1..n]

CREATE TABLE OtherJurisdiction (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , TangibleAssetValue                                 INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/InitialIntActivity/OtherJurisdiction  [1..n]

CREATE TABLE OtherJurisdiction_ResCountryCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES OtherJurisdiction(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/GLoBETax/InitialIntActivity/OtherJurisdiction/ResCountryCode  [1..5]

CREATE TABLE LTCE (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/LowTaxJurisdiction/LTCE  [0..n]

CREATE TABLE IIR (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES LTCE(id)
  , ord        INTEGER NOT NULL
  , NetGlobeIncome                                     INTEGER
  , TopUpTax                                           INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/LowTaxJurisdiction/LTCE/IIR  [1..n]

CREATE TABLE ParentEntity (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES IIR(id)
  , ord        INTEGER NOT NULL
  , TIN                                                VARCHAR(200) NOT NULL
  , TIN_issuedBy                                       VARCHAR(2)  -- 251 enum values, see meta
  , TIN_unknown                                        BOOLEAN
  , TIN_TypeOfTIN                                      VARCHAR(7) CHECK (TIN_TypeOfTIN IN ('GIR3001', 'GIR3002', 'GIR3003', 'GIR3004'))
  , ResCountryCode                                     VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , OtherOwnershipAllocation                           INTEGER NOT NULL
  , InclusionRatio                                     DECIMAL(9,6) NOT NULL
  , TopUpTaxShare                                      INTEGER NOT NULL
  , IIROffSet                                          INTEGER NOT NULL
  , TopUpTax                                           INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/LowTaxJurisdiction/LTCE/IIR/ParentEntity  [0..n]

CREATE TABLE JurisdictionSection_AdditionalDataPoint (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES JurisdictionSection(id)
  , ord        INTEGER NOT NULL
  , Description                                        VARCHAR(170)
  , Amount                                             INTEGER
  , Percentage                                         DECIMAL(9,6)
  , Text                                               VARCHAR(4000)
  , Boolean                                            BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/JurisdictionSection/AdditionalDataPoint  [0..n]

CREATE TABLE UTPRAttribution (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES GLOBEBody(id)
  , ord        INTEGER NOT NULL
  , DocSpec_DocTypeIndic                               VARCHAR(6) NOT NULL CHECK (DocSpec_DocTypeIndic IN ('OECD0', 'OECD1', 'OECD2', 'OECD3', 'OECD10', 'OECD11', 'OECD12', 'OECD13'))
  , DocSpec_DocRefId                                   VARCHAR(200) NOT NULL
  , DocSpec_CorrDocRefId                               VARCHAR(200)
);  -- /GLOBE_OECD/GLOBEBody/UTPRAttribution  [0..n]

CREATE TABLE UTPRAttribution_RecJurCode (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UTPRAttribution(id)
  , ord        INTEGER NOT NULL
  , value                                              VARCHAR(2) NOT NULL  -- 251 enum values, see meta
);  -- /GLOBE_OECD/GLOBEBody/UTPRAttribution/RecJurCode  [1..n]

CREATE TABLE Attribution (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UTPRAttribution(id)
  , ord        INTEGER NOT NULL
  , ResCountryCode                                     VARCHAR(2) NOT NULL  -- 251 enum values, see meta
  , UTPRTopUpTaxCarryForward                           INTEGER NOT NULL
  , Employees                                          INTEGER
  , TangibleAssetValue                                 INTEGER
  , UTPRPercentage                                     DECIMAL(9,6) NOT NULL
  , UTPRTopUpTaxAttributed                             INTEGER NOT NULL
  , AddCashTaxExpense                                  INTEGER NOT NULL
  , UTPRTopUpTaxCarriedForward                         INTEGER NOT NULL
);  -- /GLOBE_OECD/GLOBEBody/UTPRAttribution/Attribution  [1..n]

CREATE TABLE UTPRAttribution_AdditionalDataPoint (
  id         VARCHAR(200) PRIMARY KEY
  , parent_id  VARCHAR(200) NOT NULL REFERENCES UTPRAttribution(id)
  , ord        INTEGER NOT NULL
  , Description                                        VARCHAR(170)
  , Amount                                             INTEGER
  , Percentage                                         DECIMAL(9,6)
  , Text                                               VARCHAR(4000)
  , Boolean                                            BOOLEAN
);  -- /GLOBE_OECD/GLOBEBody/UTPRAttribution/AdditionalDataPoint  [0..n]
