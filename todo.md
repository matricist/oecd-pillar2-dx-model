- IsInsurance 따로 받기

## Product Architecture

GloBE-Model은 다음 3개의 챕터/모듈로 구성한다.

### 1. 계산모델 (Calculation Model)
- 핵심 계산 로직은 Excel Custom Functions로 제공
- 표준 입력/계산 템플릿은 Office.js Task Pane에서 생성
- GloBE Core 계산엔진을 기반으로 jurisdiction-specific rule / QDMTT override를 확장 가능하도록 설계

### 2. 신고모델 (Filing Model)
- XML 신고 데이터를 채우기 위한 표준 템플릿을 Office.js Task Pane에서 생성
- Excel Custom Function 또는 연계 기능으로 신고 대상 범위를 지정
- 지정된 Excel 범위를 바탕으로 XML을 생성하여 사용자가 선택한 로컬 폴더에 저장
- OECD GIR 및 각 국가별 local filing schema를 확장 가능한 구조로 설계

### 3. 조정모델 (Adjustment Model)
- GloBE Income / Covered Taxes 등 분모·분자 세무조정을 지원하는 모델
- 결정론적 계산엔진과 분리하여 MCP(Model Context Protocol) 기반으로 제공
- Claude in Excel 또는 GPT in Excel 등 Excel 내 LLM 클라이언트에서 사용할 수 있는 형태를 목표로 함
- LLM은 규정 해석, 조정 후보 식별, 근거 제시 및 조정 입력 지원 역할을 담당하고, 최종 수치 계산은 Calculation Model의 결정론적 엔진에서 수행하도록 설계

## IIR / Ownership Interest TODO

- `Relation.InvestmentEntities`에 `mne_allocable_ratio` 추가. Calculated 열로 처리.
- `CalculateMneAllocableRatio` 함수를 `Doc.OwnershipInterest`에 추가하고 IIR dependency에도 추가.
- 자기주식 제거 로직도 `Doc.OwnershipInterest`에 추가하고 IIR dependency에도 추가.
