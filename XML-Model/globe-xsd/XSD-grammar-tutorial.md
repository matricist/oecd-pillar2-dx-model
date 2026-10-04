# globe-xsd XSD 문법 교습서

이 문서는 `XML-Model/globe-xsd`의 XSD 3개를 읽기 위한 최소 문법만 다룬다.

- `GLOBEXML_v1.0.xsd`: 본문 스키마
- `isoglobetypes_v1.1.xsd`: ISO 국가/통화 코드 타입
- `oecdglobetypes_v5.0.xsd`: OECD 공통 타입

## 1. 먼저 읽을 것

```xml
<xsd:schema
  xmlns:globe="urn:oecd:ties:globe:v2"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:stf="urn:oecd:ties:globestf:v5"
  xmlns:iso="urn:oecd:ties:isoglobetypes:v1"
  targetNamespace="urn:oecd:ties:globe:v2"
  elementFormDefault="qualified"
  attributeFormDefault="unqualified">
```

의미:

- `xsd:`: XML Schema 문법 자체다. 예: `xsd:element`, `xsd:string`.
- `globe:`, `stf:`, `iso:`: 이 프로젝트가 정의한 타입 묶음이다.
- `targetNamespace`: 이 파일이 새로 정의하는 타입/요소가 속할 이름공간이다.
- `elementFormDefault="qualified"`: XML 문서의 요소는 네임스페이스를 가진다.
- `attributeFormDefault="unqualified"`: 속성은 보통 네임스페이스 없이 쓴다.

`GLOBEXML_v1.0.xsd`는 아래 두 파일을 가져온다.

```xml
<xsd:import namespace="urn:oecd:ties:isoglobetypes:v1"
            schemaLocation="isoglobetypes_v1.1.xsd"/>
<xsd:import namespace="urn:oecd:ties:globestf:v5"
            schemaLocation="oecdglobetypes_v5.0.xsd"/>
```

따라서 `iso:CountryCode_Type`은 ISO 파일에서, `stf:DocSpec_Type`은 OECD 공통 파일에서 찾는다.

## 2. 타입은 두 종류

### simpleType: 값 하나

텍스트, 숫자, 날짜, 코드처럼 내용이 하나인 타입이다.

```xml
<xsd:simpleType name="MessageType_EnumType">
  <xsd:restriction base="xsd:string">
    <xsd:enumeration value="GIR"/>
  </xsd:restriction>
</xsd:simpleType>
```

읽는 법: `MessageType_EnumType`은 문자열인데, 허용값은 `GIR`뿐이다.

### complexType: 하위 요소/속성을 가진 구조

```xml
<xsd:complexType name="DocSpec_Type">
  <xsd:sequence>
    <xsd:element name="DocTypeIndic" type="stf:OECDDocTypeIndic_EnumType"/>
    <xsd:element name="DocRefId" type="stf:StringMin1Max200_Type"/>
    <xsd:element name="CorrDocRefId" type="stf:StringMin1Max200_Type" minOccurs="0"/>
  </xsd:sequence>
</xsd:complexType>
```

읽는 법: `DocSpec_Type`은 `DocTypeIndic`, `DocRefId`, `CorrDocRefId` 순서의 구조다. 마지막 요소는 선택이다.

## 3. element 읽기

```xml
<xsd:element name="GLOBEBody" type="globe:GLOBEBody_Type" maxOccurs="unbounded"/>
```

- `name`: XML 문서에 나타나는 태그명.
- `type`: 값 또는 구조의 타입.
- `minOccurs`: 최소 반복 수. 생략하면 `1`.
- `maxOccurs`: 최대 반복 수. 생략하면 `1`.
- `maxOccurs="unbounded"`: 제한 없이 반복 가능.

자주 나오는 해석:

| XSD | 의미 |
| --- | --- |
| `minOccurs` 없음, `maxOccurs` 없음 | 정확히 1번 필수 |
| `minOccurs="0"` | 없어도 됨 |
| `maxOccurs="unbounded"` | 여러 번 가능 |
| `maxOccurs="3"` | 최대 3번 |
| `minOccurs="1"` | 기본값과 같아서 필수 |

`type`이 없으면 요소 안에 바로 익명 `complexType` 또는 `simpleType`이 정의된 것이다.

```xml
<xsd:element name="ReferenceJurisdiction">
  <xsd:complexType>
    <xsd:sequence>
      <xsd:element name="ResCountryCode" type="iso:CountryCode_Type"/>
      <xsd:element name="TangibleAssetValue" type="xsd:integer"/>
    </xsd:sequence>
  </xsd:complexType>
</xsd:element>
```

읽는 법: `ReferenceJurisdiction`은 별도 이름 없는 구조를 가진다.

## 4. sequence와 choice

### sequence: 이 순서 그대로

```xml
<xsd:sequence>
  <xsd:element name="MessageSpec" type="globe:MessageSpec_Type"/>
  <xsd:element name="GLOBEBody" type="globe:GLOBEBody_Type" maxOccurs="unbounded"/>
</xsd:sequence>
```

읽는 법: XML에는 `MessageSpec` 다음에 `GLOBEBody`가 온다.

`sequence` 자체에 `minOccurs="0"`이 붙으면 그 묶음 전체가 선택이다.

### choice: 이 중 하나

```xml
<xsd:choice>
  <xsd:element name="UTPRSafeHarbour">...</xsd:element>
  <xsd:element name="UTPRCalculation">...</xsd:element>
</xsd:choice>
```

읽는 법: `UTPRSafeHarbour`와 `UTPRCalculation` 중 하나만 온다.

## 5. restriction: 값 제한

`restriction`은 기존 타입을 좁힌다.

### enumeration

```xml
<xsd:restriction base="xsd:string">
  <xsd:enumeration value="GIR101"/>
  <xsd:enumeration value="GIR102"/>
</xsd:restriction>
```

허용값 목록이다.

### length

```xml
<xsd:restriction base="xsd:string">
  <xsd:minLength value="1"/>
  <xsd:maxLength value="200"/>
</xsd:restriction>
```

문자열 길이를 제한한다.

### pattern

```xml
<xsd:restriction base="xsd:string">
  <xsd:pattern value="\d{1,2}\.\d{2}"/>
</xsd:restriction>
```

정규식 제한이다. 여기서는 `0.00`, `12.34`, `99.99` 같은 형식이다. `%` 문자는 값에 넣지 않는다.

### 숫자 범위와 소수 자릿수

```xml
<xsd:restriction base="xsd:decimal">
  <xsd:minInclusive value="0"/>
  <xsd:maxInclusive value="1"/>
  <xsd:fractionDigits value="4"/>
</xsd:restriction>
```

읽는 법: 0 이상 1 이하, 소수점 이하 최대 4자리의 decimal이다.

## 6. extension: 기존 구조에 더하기

### complexContent

```xml
<xsd:complexContent>
  <xsd:extension base="globe:FilingInfo">
    <xsd:sequence>
      <xsd:element name="DocSpec" type="stf:DocSpec_Type"/>
    </xsd:sequence>
  </xsd:extension>
</xsd:complexContent>
```

읽는 법: `globe:FilingInfo`의 기존 요소들을 먼저 가진 뒤, 뒤에 `DocSpec`을 추가한다.

### simpleContent

```xml
<xsd:simpleContent>
  <xsd:extension base="stf:StringMin1Max200_Type">
    <xsd:attribute name="issuedBy" type="iso:CountryCode_Type" use="optional"/>
    <xsd:attribute name="unknown" type="xsd:boolean" use="optional"/>
    <xsd:attribute name="TypeOfTIN" type="globe:TIN_EnumType"/>
  </xsd:extension>
</xsd:simpleContent>
```

읽는 법: 본문 값은 `StringMin1Max200_Type`이고, 여기에 속성이 붙는다.

예상 XML 형태:

```xml
<TIN issuedBy="KR" TypeOfTIN="...">1234567890</TIN>
```

## 7. attribute 읽기

```xml
<xsd:attribute name="version" type="stf:StringMin1Max10_Type"/>
```

- `name`: 속성명.
- `type`: 속성값 타입.
- `use="optional"`: 선택 속성.
- `use` 생략: 기본값은 optional이다.

이 XSD에서 속성은 `issuedBy`, `unknown`, `TypeOfTIN`, `version`만 알면 된다.

## 8. annotation/documentation

```xml
<xsd:annotation>
  <xsd:documentation xml:lang="en">...</xsd:documentation>
</xsd:annotation>
```

설명문이다. XML 유효성 규칙은 아니다. 다만 코드값의 의미나 단위 설명이 들어 있으므로 읽을 때 참고한다.

## 9. 기본 타입

이 폴더에서 쓰는 `xsd:` 기본 타입은 아래뿐이다.

| 타입 | 의미 |
| --- | --- |
| `xsd:string` | 문자열 |
| `xsd:token` | 앞뒤 공백 및 연속 공백이 정규화되는 문자열 |
| `xsd:boolean` | `true/false` 또는 `1/0` |
| `xsd:integer` | 정수 |
| `xsd:decimal` | 소수 |
| `xsd:date` | 날짜, 예: `2026-08-23` |
| `xsd:dateTime` | 날짜+시간 |

## 10. 읽는 절차

1. 루트 요소를 찾는다. 이 파일의 루트는 `GLOBE_OECD`다.
2. 루트의 `complexType` 안 `sequence`를 읽는다.
3. 각 `element`의 `type`으로 이동한다.
4. `globe:` 타입은 `GLOBEXML_v1.0.xsd`, `iso:` 타입은 `isoglobetypes_v1.1.xsd`, `stf:` 타입은 `oecdglobetypes_v5.0.xsd`에서 찾는다.
5. `sequence`는 순서, `choice`는 택일, `minOccurs/maxOccurs`는 반복 횟수로 해석한다.
6. `simpleType`이면 `restriction`의 `enumeration`, `pattern`, 길이, 숫자 제한을 확인한다.
7. `complexContent/extension`이 있으면 base 타입의 내용을 먼저 읽고, extension 안의 요소를 뒤에 붙인다.
8. `simpleContent/extension`이 있으면 텍스트 값 타입에 속성이 붙는다고 읽는다.

## 11. 커버리지 체크리스트

이 교습서는 `globe-xsd`에서 실제 등장하는 XSD 태그 전체를 다룬다.

- 구조: `schema`, `import`, `element`, `complexType`, `simpleType`
- 모델: `sequence`, `choice`
- 확장: `complexContent`, `simpleContent`, `extension`
- 값 제한: `restriction`, `enumeration`, `pattern`, `minLength`, `maxLength`, `minInclusive`, `maxInclusive`, `fractionDigits`
- 속성: `attribute`
- 설명: `annotation`, `documentation`

이 교습서 밖의 XSD 기능, 예를 들어 `all`, `group`, `attributeGroup`, `list`, `union`, `any`, `key`, `unique`, `substitutionGroup`은 이 폴더에 나오지 않는다.
