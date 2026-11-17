# Output Model

## 1. 목적

Output Model은 SQL로 생성된 Output relation을 XML로 변환하기 위한 메타 모델이다.

전체 데이터 흐름은 다음과 같다.

```text
Input Relation
      │
      │ SQL
      ▼
Output Relation
      │
      │ Output Model
      ▼
XML
```

Input relation에서 Output relation으로의 변환은 SQL에서 처리한다.

따라서 XML 생성 단계에서는 별도의 business logic을 두지 않고, Output Model에 정의된 메타정보에 따라 relation을 조회하고 XML node를 생성한다.

Output Model의 역할은 크게 세 가지다.

```text
1. XML tree 구조 정의
2. XML node와 Output relation/column 연결
3. relation 간 이동 방법 정의
```

---

## 2. XML Node Meta

XML Node Meta의 각 row는 하나의 XML `element` 또는 `attribute`를 의미한다.

### 2.1 `node_id`

XML node를 식별하기 위한 고유 ID.

동일한 이름의 element가 XML의 여러 위치에 존재할 수 있으므로 `name` 대신 `node_id`를 식별자로 사용한다.

예:

```text
FilingInfo / Name
CorporateStructure / CE / ID / Name
```

두 element의 이름은 모두 `Name`이지만 서로 다른 node이므로 서로 다른 `node_id`를 가진다.

### 2.2 `name`

실제 XML에서 사용하는 element 또는 attribute 이름.

예:

```xml
<FilingCE>
```

이면:

```text
name = FilingCE
```

### 2.3 `node_kind`

node의 종류.

현재 값:

```text
element
attribute
```

예:

```xml
<TIN issuedBy="KR">123456</TIN>
```

에서는:

```text
TIN       = element
issuedBy  = attribute
```

### 2.4 `parent_node_id`

현재 node의 부모 XML node의 `node_id`.

예:

```text
node_id = 20  FilingCE
node_id = 28  TIN
```

이면:

```text
TIN.parent_node_id = 20
```

XML tree는 `node_id`와 `parent_node_id`를 이용해 구성한다.

### 2.5 `parent`

사람이 메타를 검토하기 쉽게 부모 node의 이름을 기록하는 보조 컬럼.

실제 tree 관계의 기준은 `parent_node_id`이며, `parent`는 식별이나 JOIN에 사용하지 않는다.

---

## 3. XML Type Meta

### 3.1 `value_type`

node가 실제 값을 가지는 경우 내부적으로 사용하는 값의 type.

예:

```text
string
enum
date
dateTime
bool
int
decimal
```

다른 element를 포함하기만 하는 container node는 비워둔다.

### 3.2 `enum_name`

`value_type = enum`인 경우 사용할 enumeration domain.

예:

```text
value_type = enum
enum_name  = country_code
```

실제 enum 값은 별도의 Enum Meta에서 관리한다.

예:

```text
enum_name           enum_value
------------------  ----------
country_code        KR
country_code        US
message_type_indic  GIR101
message_type_indic  GIR102
```

### 3.3 `source_xsd_type`

원래 XSD에서 해당 node가 사용한 type.

XML 생성 로직에서 직접 사용하지 않으며 원본 XSD와의 추적을 위해 저장한다.

예:

```text
stf:StringMin1Max200_Type
iso:CountryCode_Type
globe:TIN_Type
xsd:date
```

anonymous type인 경우:

```text
anonymous
```

로 기록한다.

### 3.4 `base_xsd_type`

XSD type이 다른 type을 기반으로 정의된 경우 base type을 기록한다.

예:

```xml
<xsd:extension base="stf:StringMin1Max200_Type">
```

이면:

```text
base_xsd_type = stf:StringMin1Max200_Type
```

### 3.5 `base_kind`

`base_xsd_type`과 현재 type의 관계.

현재 예상 값:

```text
extension
restriction
```

예:

```text
source_xsd_type = globe:TIN_Type
base_xsd_type   = stf:StringMin1Max200_Type
base_kind       = extension
```

---

## 4. XML Structure Meta

### 4.1 `sequence_no`

동일한 parent 아래에서 child element를 생성하는 순서.

XSD의 `sequence`를 최종 XML 구조 기준으로 flatten한 결과를 기록한다.

예:

```text
FilingCE         1
AccountingInfo   2
Period           3
NameMNE          4
AdditionalInfo   5
DocSpec          6
```

attribute에는 적용하지 않는다.

### 4.2 `choice_id`

동일한 XSD `choice`에 속하는 node들을 묶기 위한 ID.

예:

```text
UPE
└─ choice: upe
   ├─ ExcludedUPE
   └─ OtherUPE
```

이면:

```text
ExcludedUPE.choice_id = upe
OtherUPE.choice_id    = upe
```

`choice_id`는 서로 배타적인 XML alternative를 식별하는 데 사용한다.

필요한 경우 향후 choice 자체의 `minOccurs`, `maxOccurs`, `sequence_no`를 별도 Choice Meta로 분리할 수 있다.

### 4.3 `element_min_occurs`

XSD의 `minOccurs`.

해당 element가 최소 몇 번 존재해야 하는지를 나타낸다.

```text
0 = 없어도 됨
1 = 최소 한 번 필요
```

### 4.4 `element_max_occurs`

XSD의 `maxOccurs`.

예:

```text
1
unbounded
```

`unbounded`는 같은 XML element가 여러 번 나타날 수 있음을 의미한다.

반복을 관계형 모델에서 어떻게 표현할지는 element 구조에 따라 다르다.

#### 반복 scalar

예:

```xml
<ResCountryCode>KR</ResCountryCode>
<ResCountryCode>US</ResCountryCode>
```

한 occurrence가 값 하나로 끝나므로 Output relation의 list column으로 표현할 수 있다.

```text
output_listed = TRUE
```

#### 반복 structured element

예:

```xml
<TIN issuedBy="KR">111</TIN>
<TIN issuedBy="US">222</TIN>
```

각 occurrence가 value와 attribute를 함께 가지므로 별도 child relation의 여러 row로 표현한다.

```text
child_relation = tin
output_listed  = FALSE
```

즉 `maxOccurs="unbounded"`라고 해서 항상 동일한 관계형 표현을 사용하는 것은 아니다.

---

## 5. Output Value Mapping

### 5.1 `output_relation`

현재 XML node의 실제 값을 가져올 Output relation.

### 5.2 `output_column`

현재 XML node의 실제 값을 가져올 Output column.

예:

```text
output_relation = filing_ce
output_column   = res_country_code
```

이면 XML value는:

```text
filing_ce.res_country_code
```

에서 가져온다.

### 5.3 Input-to-output SQL

Input relation에서 Output relation을 만드는 SQL은 `input_output_model.sql`에 기록한다.
`output_model.csv`에는 SQL을 넣지 않고 XML node, Output relation 및 column 매핑만 유지한다.

SQL 파일에서 각 query는 다음 주석으로 대상 relation을 표시한다.

```sql
-- Output relation: globe_oecd
SELECT ...;
```

SELECT 결과의 column 이름은 해당 relation의 `output_column`과 일치해야 한다.
relation의 기술적 PK와 부모 relation을 연결하는 FK도 SELECT 결과에 포함한다.

---

## 6. Relation Navigation

XML tree 구조와 Output relation 구조는 반드시 일치하지 않는다.

따라서 XML node를 생성하면서 다른 relation으로 이동해야 하는 경우 relation navigation 정보를 별도로 정의한다.

### 6.1 `child_relation`

현재 relation context에서 현재 XML node를 생성하기 위해 이동할 relation.

예:

```text
child_relation = filing_info
```

### 6.2 `parent_key`

현재 relation에서 JOIN에 사용할 column.

### 6.3 `child_key`

`child_relation`에서 JOIN에 사용할 column.

relation 이동 조건은 항상 다음과 같다.

```text
current_relation[parent_key]
=
child_relation[child_key]
```

모든 Output relation은 다음 규칙의 기술적 PK를 가진다.

```text
<relation_name>_pk
```

PK의 논리적 type은 `integer`다. Input relation의 기술적 PK는 row 생성 시 자동 부여하고,
`input_output_model.sql`은 이 값을 대응하는 Output relation PK 이름으로 가져온다.
1:1 변환에서는 Input PK를 새로 생성하지 않고 alias로 전달한다.
`child_key`는 부모 relation PK와 같은 `integer` 값을 보관하는 FK다.

예:

```text
art_4_4_7.pk = art_4_4_7_pk
```

말단 relation처럼 현재 XML 순회에서 `parent_key`로 참조되지 않는 relation도 같은 규칙으로 PK를 가진다.
PK와 FK의 Input-to-output 매핑은 `input_output_model.sql`의 SELECT에 작성한다.

예:

```text
current relation = globe_body

child_relation = filing_info
parent_key     = globe_body_pk
child_key      = globe_body_pk
```

이면:

```text
globe_body.globe_body_pk
=
filing_info.globe_body_pk
```

조건으로 `filing_info` row를 조회한다.

조회된 row가 하나면 XML element를 한 번 생성하고, 여러 row가 조회되면 각 row에 대해 element를 반복 생성한다.

---

## 7. Relation Context

XML 생성 중에는 항상 현재 relation row를 context로 가진다.

### 7.1 `child_relation`이 없는 경우

현재 relation context를 그대로 사용한다.

예:

```text
FilingCE
└─ Role
```

`Role`이:

```text
output_relation = filing_ce
output_column   = role
```

이면 FilingCE를 생성할 때 사용하던 `filing_ce` row에서 그대로 값을 읽는다.

### 7.2 `child_relation`이 있는 경우

현재 relation row에서 `parent_key`를 읽고 child relation을 조회한 뒤, 조회된 child row를 새로운 relation context로 사용한다.

예:

```text
FilingInfo
└─ FilingCE
```

```text
child_relation = filing_ce
parent_key     = filing_info_pk
child_key      = filing_info_pk
```

---

## 8. Simple Content

일부 XML element는 text value와 attribute를 동시에 가진다.

대표적인 예가 `TIN`이다.

```xml
<TIN
    issuedBy="KR"
    unknown="false"
    TypeOfTIN="GIR3001">
    123456789
</TIN>
```

TIN은 child element는 없지만 다음 네 개의 값을 가진 구조다.

```text
tin_value
issued_by
unknown
type_of_tin
```

따라서 하나의 `tin` row가 하나의 TIN occurrence를 나타낸다.

예:

```text
TIN element
output_relation = tin
output_column   = tin_value
```

attribute는 동일한 relation에서 가져온다.

```text
issuedBy   → tin.issued_by
unknown    → tin.unknown
TypeOfTIN  → tin.type_of_tin
```

반복 TIN인 경우 `tin` relation에서 여러 row를 조회하여 각각 하나의 `<TIN>` element를 생성한다.

---

## 9. Output Constraint Meta

### 9.1 `output_nullable`

Output relation의 해당 column이 `NULL`을 허용하는지 여부.

이는 XSD의 `minOccurs` 또는 `attribute_use`와는 별개의 개념이다.

예:

```text
element_min_occurs = 0
output_nullable    = TRUE
```

일 수 있지만 반드시 동일할 필요는 없다.

XSD constraint와 relational constraint를 분리해서 관리한다.

### 9.2 `output_listed`

하나의 Output column이 scalar가 아니라 여러 값을 가지는지 나타낸다.

예:

```text
output_relation = ce_id
output_column   = res_country_code
output_listed   = TRUE
```

이면:

```text
res_country_code = [KR, US, JP]
```

와 같이 하나의 column에서 여러 XML occurrence의 값을 제공한다.

`output_listed`는 XML element가 반복되는지 자체를 의미하지 않는다.

반복 여부는:

```text
element_max_occurs
```

가 정의한다.

반복이 별도의 child relation row로 표현되는 경우에는:

```text
output_listed = FALSE
```

이다.

예:

```text
TIN
element_max_occurs = unbounded
child_relation     = tin
output_listed      = FALSE
```

### 9.3 `string_min_length`

문자열의 최소 길이.

예:

```text
1
```

### 9.4 `string_max_length`

문자열의 최대 길이.

예:

```text
10
170
200
4000
```

### 9.5 `attribute_use`

attribute의 필수 여부.

예:

```text
optional
required
```

element의 `minOccurs`, `maxOccurs`와 별도로 관리한다.

XSD에서 `use`가 생략된 attribute는 기본적으로:

```text
optional
```

로 처리한다.

### 9.6 `description`

node에 대한 설명.

XSD의 `annotation/documentation` 또는 내부 설명을 기록한다.

XML 생성에는 직접 영향을 주지 않는다.

---

## 10. XML Generation

XML 생성은 relation context를 가지고 XML tree를 재귀적으로 순회하면서 수행한다.

기본 흐름은 다음과 같다.

```text
generate(node, current_row)
```

### 10.1 현재 XML node 확인

`node_id`를 기준으로 node meta를 읽는다.

### 10.2 Relation 이동

`child_relation`이 존재하면:

```text
current_row[parent_key]
=
child_relation[child_key]
```

조건으로 child relation을 조회한다.

조회된 각 row를 새로운 relation context로 사용한다.

`child_relation`이 없으면 기존 context를 유지한다.

### 10.3 Element 생성

현재 node가 `element`이면 XML element를 생성한다.

### 10.4 Attribute 생성

현재 node의 attribute child들을 조회하여 attribute 값을 기록한다.

### 10.5 Text value 생성

`value_type`이 존재하면:

```text
output_relation.output_column
```

에서 값을 가져와 element text로 기록한다.

`output_listed = TRUE`이면 list의 각 값을 동일한 XML element occurrence로 변환한다.

### 10.6 Child element 생성

child element들을:

```text
sequence_no
```

순서대로 재귀 생성한다.

### 10.7 Occurrence 검증

생성된 XML element 수가:

```text
element_min_occurs
element_max_occurs
```

조건을 만족하는지 검증한다.

---

## 11. Root

XML 생성은 root node인 `GLOBE_OECD`에서 시작한다.

초기 설정:

```text
root_node_id  = 1
root_relation = globe_oecd
```

즉:

```text
GLOBE_OECD
+
globe_oecd row
```

를 최초 context로 두고 XML tree를 순회한다.

그 이후 relation 이동은 각 node의:

```text
child_relation
parent_key
child_key
```

를 따른다.

---

## 12. 설계 원칙 요약

Output Model의 핵심 규칙은 다음과 같다.

```text
XML 구조
→ node_id / parent_node_id / sequence_no / choice_id

XSD cardinality
→ element_min_occurs / element_max_occurs

XML 값
→ output_relation / output_column

relation 이동
→ child_relation / parent_key / child_key

relation NULL 제약
→ output_nullable

한 column 내 반복 scalar
→ output_listed

문자열 제약
→ string_min_length / string_max_length

attribute 필수 여부
→ attribute_use
```

반복 구조는 다음 기준으로 나눈다.

```text
Repeated scalar
→ 하나의 output column에 list
→ output_listed = TRUE

Repeated structured value
→ child relation의 여러 row
→ output_listed = FALSE
```

예:

```text
ResCountryCode
= repeated scalar
= [KR, US, JP]

TIN
= repeated structured value
= 여러 tin row
```
