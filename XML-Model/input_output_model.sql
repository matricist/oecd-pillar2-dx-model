-- Output relation: globe_oecd
-- One message_header row produces one globe_oecd row.

SELECT
    mh.message_header_pk AS globe_oecd_pk,
    mh.version AS version,
    mh.sending_entity_in AS sending_entity_in,
    mh.transmitting_country AS transmitting_country,
    mh.receiving_country AS receiving_country,
    mh.message_type AS message_type,
    mh.warning AS warning,
    mh.contact AS contact,
    mh.message_ref_id AS message_ref_id,
    mh.message_type_indic AS message_type_indic,
    mh.reporting_period AS reporting_period,
    mh.timestamp AS timestamp
FROM message_header AS mh
WHERE mh.message_header_pk = @message_header_pk;


-- Output relation: globe_body
-- One globe_body input row produces one GLOBEBody occurrence.

SELECT
    gb.globe_body_pk AS globe_body_pk,
    gb.message_header_pk AS globe_oecd_pk
FROM globe_body AS gb
WHERE gb.message_header_pk = @message_header_pk;


-- FilingInfo branch
-- FilingInfo and its required one-to-one child elements are stored in one input row.

-- Output relation: filing_info
SELECT
    fi.filing_info_pk AS filing_info_pk,
    fi.globe_body_pk AS globe_body_pk,
    fi.name_mne AS name_mne,
    fi.additional_info AS additional_info
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
WHERE gb.message_header_pk = @message_header_pk;


-- Output relation: filing_ce
SELECT
    fi.filing_info_pk AS filing_ce_pk,
    fi.filing_info_pk AS filing_info_pk,
    ce.jurisdiction_code AS res_country_code,
    ce.name AS name,
    fi.filing_ce_role AS role
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
JOIN company_entities AS ce
    ON ce.company_entities_pk = fi.filing_ce_company_entities_pk
WHERE gb.message_header_pk = @message_header_pk;


-- Output relation: tin
-- This branch maps the Filing Constituent Entity TIN from company_entities.
SELECT
    fi.filing_info_pk AS tin_pk,
    fi.filing_info_pk AS filing_ce_pk,
    ce.tin_value AS tin_value,
    ce.issued_by AS issued_by,
    ce.unknown AS unknown,
    ce.type_of_tin AS type_of_tin
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
JOIN company_entities AS ce
    ON ce.company_entities_pk = fi.filing_ce_company_entities_pk
WHERE gb.message_header_pk = @message_header_pk;


-- Output relation: accounting_info
SELECT
    fi.filing_info_pk AS accounting_info_pk,
    fi.filing_info_pk AS filing_info_pk,
    fi.cfs_of_upe AS cfs_of_upe,
    fi.fas AS fas,
    fi.currency AS currency
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
WHERE gb.message_header_pk = @message_header_pk;


-- Output relation: period
SELECT
    fi.filing_info_pk AS period_pk,
    fi.filing_info_pk AS filing_info_pk,
    fi.period_start AS start,
    fi.period_end AS end
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
WHERE gb.message_header_pk = @message_header_pk;


-- Output relation: doc_spec
SELECT
    fi.filing_info_pk AS doc_spec_pk,
    fi.filing_info_pk AS filing_info_pk,
    fi.doc_type_indic AS doc_type_indic,
    fi.doc_ref_id AS doc_ref_id,
    fi.corr_doc_ref_id AS corr_doc_ref_id
FROM filing_info AS fi
JOIN globe_body AS gb
    ON gb.globe_body_pk = fi.globe_body_pk
WHERE gb.message_header_pk = @message_header_pk;
