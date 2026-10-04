
#### Group Hash Code

Stateless Entity는 해당 Entity가 마치 별도 MNE Group을 형성하는 것처럼 계산한다. 즉, Entity 단위의 계산을 요구하기 때문에 가장 harsh한 분류에 속한다. 즉, 모든 JV, MOCE, IE 분류의 부분집합에 속하게 된다.

MOSG 및 단독 MOCE는 상술했듯이, UPE 산하의 MOSG일 수 있고 JV 산하의 MOSG일 수 있다. UPE 산하인 경우 MOSG와 JV의 비교는 의미가 없고, JV 산하인 경우 MOSG는 최소한 JV 그룹의 JV를 포함하지 않으므로 해당 JV그룹의 진부분집합에 해당한다. 따라서 GroupId를 정함에 있어 MOSG가 JV에 우선한다고 볼 수 있다.

위 두 문단을 종합했을 때 GroupId 결정 우선순위는 다음과 같다.
Stateless > MOSG > JV
참고로 투자기업은 국가코드만으로 구분이 되기 때문에 별도의 GroupId를 필요로 하지 않는다.

따라서 어떤 Entity의 EntityId가 1~9999라고 가정하고 JurisdictionCode, IE그룹여부, GroupId를 가지고 Group Hash Code를 만든다면 다음과 같다:
1. 구성기업인 경우
{GroupId}(null인 경우 "0000")+{JurisdictionCode}(Null인 경우 "00")+{T/F}
2. 구성기업 또는 member of JV Group에 해당하지 않는 경우
null

GroupId는 다음과 같다. (1에서 4순으로 검토하며 해당 사항이 있는 경우 해당 번호에서 검토를 중지한다.)
1. Stateless Entity에 해당하는 경우
{EntityId}
2. 단독 MOCE 또는 MOSG member인 경우
{Top-level MOPE ID}
3. member of JV Group인 경우
{Top-level JV ID}
4. 그 외의 경우(구성기업도 member of JV Group도 아닌 Entity 포함)
null

Group Hash Code를 기준으로 Full Calc 테이블을 만들자.