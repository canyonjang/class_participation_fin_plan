import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

st.set_page_config(page_title="라이브 수업 참여", layout="wide")

# =====================================================================
# [교수님 수정 구간 ①] 수업 목록과 과목 연결
# ---------------------------------------------------------------------
# 왼쪽(키)  : 학생/교수 화면에 보이는 '수업 이름'
# 오른쪽(값): 그 수업이 사용할 '문제은행 이름'
#   → 같은 과목을 여러 분반이 공유하면 오른쪽 값을 똑같이 적으면 됩니다.
# =====================================================================
CLASS_COURSE = {
    "인하대 소비자재무설계":    "재무설계1",
    "숙대 소비자재무설계1_001": "재무설계1",
    "숙대 소비자재무설계1_002": "재무설계1",
    "인하대 가계자산투자설계":  "가계자산투자설계",
    "숙대 소비자재무설계2_001": "재무설계2",
    "숙대 소비자재무설계2_002": "재무설계2",
}
CLASS_LIST = list(CLASS_COURSE.keys())


# =====================================================================
# [교수님 수정 구간 ②-A] 재무설계1 문제은행  (item id: 1 ~ 99)
# =====================================================================

def get_cfp1_data():
    return {
        2: [ # 2주차 수업 자료 (기존 9개)
            {"type": "balance", "id": 1, "q": "더 선호하는 삶의 형태는?", "opt": ["A: 돈은 평균 이상이나 늘 불만족한 삶", "B: 자산은 부족해도 스스로 만족하는 삶"]},
            {"type": "qr_survey", "id": 2, "title": "나의 경제적 복지 유형 파악",
                "questions": [
                    {"q": "객관적으로 판단할 때, 나의 소득과 소비생활 수준은?", "opt": ["매우 나쁜 상황이다", "나쁜 상황이다", "좋은 상황이다", "매우 좋은 상황이다"]},
                    {"q": "주관적으로 생각하면, 나의 소득과 소비생활 수준은?", "opt": ["매우 불만족스럽다", "불만족스럽다", "만족스럽다", "매우 만족스럽다"]}
                ]
            },
            {"type": "balance", "id": 3, "q": "로또 당첨 시 더 기대되는 변화는?", "opt": ["A: 소비행태, 자동차 등 외적인 변화", "B: 목표, 가치관 등 내적인 변화"]},
            {"type": "balance", "id": 4, "q": "누구의 조언을 더 신뢰하시나요?", "opt": ["A: 저축을 강조하는 부모님의 경험", "B: 투자 방법을 알려주는 유튜브 및 경제신문의 정보"]},
            {"type": "balance", "id": 5, "q": "더 화나는 배우자의 비밀은?", "opt": ["A: 나 몰래 자기 부모님 용돈 드리기", "B: 나 몰래 비상금으로 주식 투자하기"]},
            {"type": "quiz", "id": 6, "q": "동메달(7.1점)이 은메달(4.8점)보다 행복한 이유는?", "opt": ["상향 비교", "하향 비교", "절대적 만족"], "ans": "하향 비교"},
            {"type": "balance", "id": 7, "q": "더 불행한 상황은?", "opt": ["A: 나는 20% 수익을 냈는데, 가장 친한 친구는 100% 수익(대박)을 냄", "B: 나는 10% 손실을 봤는데, 주변 사람들은 모두 나보다 더 큰 손실을 봄"]},
            {"type": "quiz", "id": 8, "q": "조사 결과 가장 낮은 점수를 기록한 불안 영역은?", "opt": ["필수지출 불안", "재정안정성 불안", "부채 불안"], "ans": "필수지출 불안"},
            {"type": "quiz", "id": 9, "q": "주부들이 지출 스트레스보다 더 강하게 느끼는 것은?", "opt": ["소득 스트레스", "자산 스트레스", "부채 스트레스"], "ans": "자산 스트레스"}
        ],
        3: [# 1. 밸런스 게임: 목표의 구체성 (강의안 1-2p)
    {   "type": "balance", "id": 10,
        "q": "어떤 방식으로 목표를 세우는 것이 더 효과적일까요?",
        "opt": ["A: '언젠가 부자가 되겠다'는 원대한 꿈", "B: '3년 내 3천만원 모으기'처럼 구체적인 계획"]},
    # 2. 밸런스 게임: 부부 재무 대화와 솔직함 (강의안 14-17p)
    {   "type": "balance", "id": 11,
        "q": "부부 사이의 재무 관리에 대한 당신의 생각은?",
        "opt": ["A: 돈 문제로 다투더라도 매달 투명하게 공유한다", "B: 평화를 위해 일정 금액의 비자금은 각자 관리한다"]},
    # 3. 퀴즈: 20대 가계수지지표 가이드라인 (강의안 22p)
    {   "type": "quiz", "id": 12,
        "q": "20대 사회초년생의 경우, 총소득 대비 지출 비중(가계수지지표)의 가이드라인은 몇 % 이하인가요?",
        "opt": ["50% 이하", "70% 이하", "80% 이하", "90% 이하"],
        "ans": "50% 이하"},
    # 4. 퀴즈: 금융투자성향지표의 정의 (강의안 24p)
    {   "type": "quiz", "id": 13,
        "q": "총저축액 중에서 펀드나 주식처럼 원금이 보장되지 않는 투자상품에 넣는 금액의 비중을 뜻하는 지표는?",
        "opt": ["가계수지지표", "저축성향지표", "금융투자성향지표", "부채부담지표"],
        "ans": "금융투자성향지표"},
    # 5. 밸런스 게임: 남과의 비교 vs 나의 기준 (강의안 26p)
    {   "type": "balance", "id": 14,
        "q": "당신이 더 행복감을 느낄 것 같은 상황은?",
        "opt": ["A: 내 자산이 작년보다 10% 늘어남", "B: 내 자산은 20% 늘었지만, 친구 자산은 100% 늘어남"]},
    # 6. 퀴즈: 투자비율이 만족에 미치는 영향 (강의안 27p)
    {   "type": "quiz", "id": 15,
        "q": "재무적 만족도에 가장 큰 영향을 미치는 '투자비율'은 가계의 어떤 측면을 보여주는 지표인가요?",
        "opt": ["안정성", "유동성", "성장성", "도덕성"],
        "ans": "성장성"}
],
        4: [
    # 1. 밸런스 게임: 복리의 마법 (강의안 1-5p)
    # [근거] 어마어마한 수익률보다 '오랫동안 괜찮은 수준'을 유지하는 것이 복리의 핵심
    {   "type": "balance", "id": 16,
        "q": "당신이 추구하는 투자 스타일은?",
        "opt": ["A: 단기간에 엄청난 수익률을 내고 졸업하기", "B: 적당한 수익률이라도 수십 년간 꾸준히 유지하기"]},
    # 2. 밸런스 게임: 소비 부자 vs 자산 부자 (강의안 6p)
    # [근거] 부(Wealth)는 쓰지 않은 소득이며, 나중에 무언가를 사기 위한 선택권임
    {   "type": "balance", "id": 17,
        "q": "당신이 더 꿈꾸는 부자의 모습은?",
        "opt": ["A: 좋은 차와 집으로 부를 과시하는 '소비 부자'", "B: 겉은 검소하지만 언제든 쓸 수 있는 선택권을 가진 '자산 부자'"]},
    # 3. 퀴즈: 저축의 심리적 정의 (강의안 8p)
    # [근거] 저축 = 소득 - 자존심. 겸손을 늘리는 것이 저축의 핵심
    {   "type": "quiz", "id": 18,
        "q": "모건 하우절이 정의한 '저축'의 공식으로 옳은 것은?",
        "opt": ["저축 = 소득 - 소비", "저축 = 소득 - 자존심", "저축 = 투자수익 - 소비", "저축 = 소득 - 생활비"],
        "ans": "저축 = 소득 - 자존심"},
    # 4. 퀴즈: 매몰 비용의 함정 (강의안 11p)
    # [근거] 과거의 노력에 얽매이지 말고, 상황이 변하면 계획을 가차 없이 버려야 함
    {   "type": "quiz", "id": 19,
        "q": "과거의 노력에 얽매여 잘못된 의사결정을 하게 만드는 '사악한 역할'을 하는 비용은?",
        "opt": ["기회 비용", "고정 비용", "매몰 비용", "가변 비용"],
        "ans": "매몰 비용"},
    # 5. 밸런스 게임: 투자의 대가 - 입장료 vs 벌금 (강의안 12-17p)
    # [근거] 변동성과 불확실성은 투자의 성공을 위한 '입장료'임
    {   "type": "balance", "id": 20,
        "q": "주가 폭락으로 내 자산이 하락했을 때, 당신의 생각은?",
        "opt": ["A: 내가 뭔가 잘못한 것에 대한 '벌금'을 내고 있다", "B: 미래의 높은 수익을 얻기 위한 '입장료'를 내고 있다"]},
    # 6. 밸런스 게임: 나만의 게임 (강의안 18-19p)
    # [근거] 나와 다른 게임을 하는 사람들의 행동에 설득당하지 않는 것이 중요함
    {   "type": "balance", "id": 21,
        "q": "주변 사람들이 단기 투자로 대박이 났다는 소문을 들었을 때?",
        "opt": ["A: 나도 소외되지 않게 투자 방식을 바꾼다", "B: 그들과 나는 '다른 게임'을 하고 있음을 인정하고 내 길을 간다"]},
    # 7. 퀴즈: 자기과신의 특성 (강의안 20p)
    # [근거] 범위를 좁게 설정할수록(확신이 클수록) 자기과신 성향이 강함
    {   "type": "quiz", "id": 22,
        "q": "자기과신(Overconfidence) 성향이 강한 사람의 특징으로 옳은 것은?",
        "opt": ["자신의 실수를 잘 예측한다", "정답의 범위를 아주 넓게 설정한다", "자신의 예측 범위에 대한 확신이 커서 범위를 좁게 잡는다", "전문가의 조언을 맹신한다"],
        "ans": "자신의 예측 범위에 대한 확신이 커서 범위를 좁게 잡는다"}
],
   5: [
    # 1. 신경증(Neuroticism): 평온함 유지 vs 빠른 대응
    # [근거] 신경증 점수가 높을수록 재무 통제력이 낮아 웰빙에 부정적인 영향을 미침
    {   "type": "balance", "id": 23,
        "q": "보유한 주식이 하루 만에 10% 폭락했다면?",
        "opt": ["A: 일시적인 변동일 뿐! 차분하게 시장을 관망한다", "B: 불안해서 일이 손에 안 잡힌다! 즉시 매도하거나 대응책을 찾는다"]},
    # 2. 개방성(Openness): 새로운 투자 vs 익숙한 투자
    # [근거] 개방성이 높을수록 새로운 경험에 긍정적이며 위험 허용도가 높음
    {   "type": "balance", "id": 24,
        "q": "생소하지만 유망해 보이는 신흥국 주식 투자 기회가 왔다면?",
        "opt": ["A: 새로운 기술과 시장에 과감히 투자한다", "B: 내가 잘 아는 익숙하고 안전한 종목에만 집중한다"]},
    # 3. MBTI J(판단) vs P(인식): 자금 관리 스타일
    # [근거] J형은 신속한 의사결정을 선호하고, P형은 즉흥성 때문에 가계부 작성 등 자금 관리에 소홀할 수 있음
    {   "type": "balance", "id": 25,
        "q": "나의 평소 자금 관리 스타일은?",
        "opt": ["A: 가계부를 꼼꼼히 쓰고 계획에 따라 신속하게 결정한다 (J형)",
            "B: 가계부보다는 상황에 맞춰 즉흥적으로 유연하게 관리한다 (P형)"]},
    # 4. 퀴즈: BIT(행동 투자자 유형) 모델
    # [근거] 추종자(Friendly Follower)는 스스로의 투자 철학이 부족해 유행을 따르며, 남들보다 뒤처질까 봐 후회 회피 성향을 보임
    {   "type": "quiz", "id": 26,
        "q": "BIT 모델 중 '최근의 유행을 따르며 남들이 돈 벌 때 소외될까 봐 무리하게 투자'하는 유형은?",
        "opt": ["보존가 (Passive Preserver)", "추종자 (Friendly Follower)", "독립가 (Independent Individualist)", "축적가 (Active Accumulator)"],
        "ans": "추종자 (Friendly Follower)"},
    # 5. 정보 인식의 틀: 관계 중심 vs 범주 중심
    # [근거] 동양인은 대상 간의 연관성(원숭이-바나나)을, 서양인은 독립적 객체의 공통 성질(원숭이-판다: 포유류)을 중시함
    {   "type": "balance", "id": 27,
        "q": "원숭이, 판다, 바나나 중 두 가지를 묶어야 한다면 당신의 선택은?",
        "opt": ["A: 원숭이와 판다", "B: 원숭이와 바나나"]},
    # 6. 위험 추구의 근거: 나의 능력 vs 주변의 도움
    # [근거] 쿠션(Cushion) 가설은 재무적 위험에 빠져도 도와줄 사회적 네트워크가 있다고 믿을 때 위험 추구 성향이 강해진다고 설명함
    {   "type": "balance", "id": 28,
        "q": "내가 위험한 투자를 결정할 때, 나는 어떤 선택을 하나?",
        "opt": ["A: 나의 분석 능력과 판단을 믿고 배팅한다",
            "B: 실패해도 나를 도와줄 가족이나 친구가 있다고 믿고 배팅한다"]}
],
  6: [
    # 1. 밸런스 게임: 상식 vs 과학 (과학적 태도의 중요성)
    {   "type": "balance", "id": 29,
        "q": "내가 생각하는 재무 관리의 정답은?",
        "opt": ["A: 월급의 절반(50%)도 저축 못 하면 재무설계 실패다! 무조건 아껴서 수치를 맞추는 것이 철칙이다.",
            "B: 50%라는 수치보다 내 나이, 부양가족, 고정 지출 데이터를 분석해 도출한 '나만의 저축률'이 더 중요하다."
        ]
    },
    # 2. 밸런스 게임: 양적 데이터 vs 질적 데이터 (양화의 핵심)
    {   "type": "balance", "id": 30,
        "q": "완벽한 재무설계를 위해 더 중요한 데이터는?",
        "opt": ["A: 숫자는 거짓말하지 않는다! 통장 잔고, 대출 이자율, 자산 구성비 등 정확한 수치 데이터가 우선이다.",
            "B: 숫자 너머를 봐야 한다! 돈을 쓸 때 느끼는 행복감, 미래에 대한 불안감, 소비 습관의 이유 등 심리적 데이터가 우선이다."
        ]
    },
    # 3. 밸런스 게임: 상관관계의 함정과 비판적 사고
    {   "type": "balance", "id": 31,
        "q": "뉴스에서 '빨간색 차가 흰색 차보다 사고율이 높다'는 보도를 보았다. 당신의 결론은?",
        "opt": ["A: 빨간색이라는 색상 자체가 운전자를 흥분하게 만들어 사고를 유발하므로, 안전을 위해 내 차를 흰색으로 도색하겠다.",
            "B: 혹시 성격이 급하거나 과격한 운전자가 빨간색 차를 더 선호하는 것은 아닐까?"
        ]
    },
    # 4. 퀴즈: 가설의 성립 조건
    {   "type": "quiz", "id": 32,
        "q": "'내일 코스피 지수는 이란 전쟁으로 5% 하락할 것이다.' 이 문장은 올바른 가설일까요?",
        "opt": ["가설이다", "가설이 아니다"],
        "ans": "가설이 아니다"
    },
    # 5. 밸런스 게임: 재무적 아노미의 대처
    {   "type": "balance", "id": 33,
        "q": "높은 재무적 열망과 낮은 현실적 기대 사이에서 격차를 느낄 때 당신의 선택은?",
        "opt": ["A: 목표(열망)를 낮추어 현실적인 기대에 순응한다",
            "B: 수단을 가리지 않고 열망하는 목표를 달성하려 노력한다"
        ]
    }
],
  7: [
    # 1. 밸런스 게임: 부채 관리의 태도
    {   "type": "balance", "id": 34,
        "q": "대출(부채)을 바라보는 나의 기본적인 시각은?",
        "opt": ["A: 빚은 무조건 나쁜 것! 무서우니 아예 빌리지 말아야 한다",
            "B: 내 상환 능력 안에서라면 자산을 불리기 위해 적극 활용해야 한다"
        ]
    },
    # 2. 밸런스 게임: 금융이해력의 자화상
    {   "type": "balance", "id": 35,
        "q": "투자를 결정할 때 내가 더 신뢰하는 지표는?",
        "opt": ["A: 철저하게 공부해서 쌓은 '객관적 금융 지식'",
            "B: 시장의 흐름을 읽는 나만의 직관과 '투자 촉(메사키)'"
        ]
    }
],
  8: [
    # 1. 밸런스 게임: AI 시대의 탐색 비용 (11-13p)
    {   "type": "balance", "id": 36,
        "q": "금융 상품을 고를 때 당신이 더 중요하게 생각하는 가치는?",
        "opt": ["A: AI를 활용해 최대한 많은 대안을 빠르게 요약받는 '효율성'",
            "B: 시간이 걸리더라도 직접 원문 출처를 대조하고 확인하는 '정확성'"]
    },
    # 2. 밸런스 게임: 정보 탐색의 딜레마 (14-15p)
    {  "type": "balance", "id": 37,
        "q": "관심 있는 금융 투자 정보를 발견했을 때 나의 행동은?",
        "opt": ["A: 나중에 보기 위해 일단 모두 저장해둔다 (쓴도쿠 성향)",
            "B: 지금 당장 읽을 수 있는 핵심 정보 1~2개만 남긴다 (큐레이션 성향)"]
    },
    # 3. 퀴즈: 소비자 휴리스틱의 정의 (21-22p)
    {   "type": "quiz", "id": 38,
        "q": "합리적인 기준에 근거해 비교하기보다 직관적으로 빠르게 내리는 결정의 도구를 무엇이라 하나요?",
        "opt": ["바이어스(Bias)", "휴리스틱(Heuristic)", "알고리즘(Algorithm)", "큐레이션(Curation)"],
        "ans": "휴리스틱(Heuristic)"
    },
    # 4. 밸런스 게임: 소비자 휴리스틱의 종류 (24, 26p)
    {   "type": "balance", "id": 39,
        "q": "새로운 적금 상품에 가입해야 한다면?",
        "opt": ["A: 이자율이 조금 낮아도 늘 이용하던 주거래 은행을 선택한다 (인지)",
            "B: 다른 조건은 안 본다! 무조건 이자율이 가장 높은 곳을 찾아간다 (제거)"]
    },
    # 5. 퀴즈: 행동 변화의 5단계(TTM) (37-38p)
    {  "type": "quiz", "id": 40,
        "q": "나쁜 재무 행동을 중단한 지 '6개월 이상' 경과하여 변화를 지속하려 노력하는 단계는?",
        "opt": ["계획 단계", "준비 단계", "행동 단계", "유지 단계"],
        "ans": "유지 단계"
    },
    # 6. 밸런스 게임: 행동 변화의 전략 (41-43p)
    {   "type": "balance", "id": 41,
        "q": "나의 나쁜 소비 습관을 고치기 위해 당신에게 더 효과적인 방법은?",
        "opt": ["A: 일주일간 절약에 성공하면 나에게 맛있는 선물을 준다 (보상)",
            "B: 충동구매를 할 때마다 집안 화장실 청소를 도맡아 한다 (벌칙)"]
    },
    # 7. 밸런스 게임: 인지부조화와 자존심 (44-46p)
    {   "type": "balance", "id": 42,
        "q": "정말 꼼꼼히 분석해서 산 주식이 폭락했다면, 나의 첫 마디는?",
        "opt": ["A: '거봐, 내 분석이 틀릴 리 없어. 시장 상황이 너무 안 좋네!' (자기선택 강화)",
            "B: '내가 놓친 정보가 있었나? 추천해준 유튜버 말만 믿는 게 아니었는데..' (남탓/원인분석)"]
    }
]
    }


# =====================================================================
# [교수님 수정 구간 ②-B] 가계자산투자설계 문제은행  (item id: 101 ~ 199)
# ---------------------------------------------------------------------
# 아래 주석(#)을 지우고 내용을 채우시면 바로 사용할 수 있습니다.
# 형식은 위 재무설계1과 100% 동일합니다.
# =====================================================================

def get_invest_data():
    return {
          1: [# 1. 밸런스 게임: 목표의 구체성
    {   "type": "balance", "id": 101,
        "q": "어떤 방식으로 목표를 세우는 것이 더 효과적일까요?",
        "opt": ["A: '언젠가 부자가 되겠다'는 원대한 꿈", "B: '3년 내 3천만원 모으기'처럼 구체적인 계획"]},
        # 2. 퀴즈: 20대 가계수지지표 가이드라인
    {   "type": "quiz", "id": 102,
        "q": "20대 사회초년생의 경우, 총소득 대비 지출 비중(가계수지지표)의 가이드라인은 몇 % 이하인가요?",
        "opt": ["50% 이하", "70% 이하", "80% 이하", "90% 이하"],
        "ans": "50% 이하"},
           ],
        
  2: [# 1. 밸런스 게임: 원금손실 위험 vs 실질가치 하락 위험
    # [의미] 저축은 원금이 보장되지만, 물가상승률이 금리보다 높으면 실질가치가 줄어듦.
    #        "위험을 피한 선택"도 실은 다른 위험을 지는 것임을 깨닫게 하는 문항.
    #        보통 A가 많이 나오는데, 그때 "A도 손실을 보고 있다"고 짚어주면 반응이 큼.
    {   "type": "balance", "id": 103,
        "q": "물가가 연 4% 오르는데 예금 금리는 연 2%입니다. 당신의 선택은?",
        "opt": ["A: 원금이 보장되는 예금에 넣고 마음 편히 지낸다",
                "B: 원금손실을 감수하더라도 투자해 실질가치를 지킨다"]},

    # 2. 퀴즈: 투자와 투기의 구분 기준
    # [정답] 기본적 분석에 근거해 장기적으로 수익을 얻고자 하는 행위
    # [근거] 투기는 가격이 단기에 급등할 것이라는 단순한 믿음에 기초함 (강의안 3p)
    {   "type": "quiz", "id": 104,
        "q": "강의안이 정의한 '투자(investment)'와 '투기(speculation)'를 가르는 기준은?",
        "opt": ["원금손실 가능성이 있는지 여부",
                "기본적 분석에 근거해 장기적 수익을 추구하는지 여부",
                "투자 금액의 크기",
                "금융기관을 통해 거래하는지 여부"],
        "ans": "기본적 분석에 근거해 장기적 수익을 추구하는지 여부"},

    # 3. 밸런스 게임: 교과서의 위험 vs 개인이 느끼는 위험
    # [의미] 교과서의 대표 위험지표는 변동성이지만, 개인은 '원금손실 가능성'을 위험으로 인식함.
    #        변동성 지표의 한계(수익이 난 경우도 위험으로 계산함)를 자연스럽게 도입.
    {   "type": "balance", "id": 105,
        "q": "'위험한 투자'라는 말을 들었을 때, 당신이 떠올리는 것은?",
        "opt": ["A: 수익률이 위아래로 심하게 흔들리는 것 (변동성)",
                "B: 원금을 까먹을 수 있다는 것 (원금손실 가능성)"]},

    # 4. 밸런스 게임: 연봉의 흐름 (카너먼 실험 재현)
    # [의미] 총액과 할인율만 따지면 A가 합리적(현재의 돈이 더 가치 있음).
    #        그런데 다수는 B를 선택함 → 손실회피. 임금이 줄어드는 것을 못 견디기 때문.
    # [수업 팁] 강의안 12p의 실제 사례. 결과 발표 후 "왜 B를 골랐나" 물어보면 토론이 살아남.
    {   "type": "balance", "id": 106,
        "q": "3년간 총액이 같은 두 개의 연봉 계약, 당신의 선택은?",
        "opt": ["A: 첫해 1억원 → 둘째해 7천만원 → 셋째해 5천만원",
                "B: 첫해 5천만원 → 둘째해 7천만원 → 셋째해 1억원"]},

    # 5. 밸런스 게임: 목표별 계좌 분리 vs 통합 관리
    # [의미] 행동경제학은 개인이 목표별로 계좌를 분리해 관리하는 경향(심적 회계)을 지적함.
    #        강의안은 이를 부정하지 않고, 오히려 목표별로 위험수준을 다르게 설정하라고 권함.
    {   "type": "balance", "id": 107,
        "q": "당신의 자금 관리 방식에 더 가까운 쪽은?",
        "opt": ["A: 여행자금·비상금·학자금 통장을 따로 만들어 관리한다",
                "B: 어차피 같은 내 돈, 한 계좌에 모아 전체 수익률만 본다"]},

    # 6. 밸런스 게임: 투자기간과 위험자산
    # [의미] 투자기간이 짧으면 위험자산이 매우 위험해짐. 2008년 위기 때 회복에 4-5년이 걸렸음.
    #        같은 상품이라도 '언제 쓸 돈인가'에 따라 정답이 달라진다는 점을 체감시키는 문항.
    {   "type": "balance", "id": 108,
        "q": "1년 뒤 전세보증금으로 쓸 5천만원, 어디에 둘까요?",
        "opt": ["A: 1년이면 짧지 않다. 우량주에 투자해 수익을 노린다",
                "B: 무조건 예금이다. 1년 뒤 반토막이면 이사를 못 간다"]},

    # 7. 퀴즈: 금리위험의 방향
    # [정답] 금리가 상승하면 채권가격이 하락한다
    # [근거] 시장위험 중 금리위험의 정의 (강의안 29p)
    {   "type": "quiz", "id": 109,
        "q": "채권 투자에서 '금리위험'이란 무엇 때문에 손실이 발생하는 위험인가요?",
        "opt": ["금리가 상승해 채권가격이 하락하는 것",
                "금리가 하락해 채권가격이 하락하는 것",
                "발행기업이 부도를 내는 것",
                "환율이 변동하는 것"],
        "ans": "금리가 상승해 채권가격이 하락하는 것"}
],
  3: [# 1. 퀴즈: GDP에 포함되는 것
    # [정답] 외국 자동차 회사가 한국 공장에서 생산한 자동차
    # [근거] "한 국가 안에서" 생산된 것이므로 국내 외국기업 생산도 포함.
    #        중고품(과거 생산분)과 중간재는 제외됨 (강의안 2p)
    {   "type": "quiz", "id": 110,
        "q": "다음 중 우리나라 GDP에 포함되는 것은?",
        "opt": ["작년에 산 중고차를 올해 되판 금액",
                "외국 자동차 회사가 한국 공장에서 생산한 자동차",
                "자동차 제조에 들어간 타이어(중간재) 가격",
                "삼성전자가 베트남 공장에서 생산한 스마트폰"],
        "ans": "외국 자동차 회사가 한국 공장에서 생산한 자동차"},

    # 2. 밸런스 게임: GDP는 삶의 질을 말해주는가
    # [의미] 3면 등가의 원칙으로 GDP는 소득이기도 하지만,
    #        가사노동·환경·분배는 잡히지 않음. 지표의 한계를 논의하는 문항.
    {   "type": "balance", "id": 111,
        "q": "GDP가 늘어나면 우리 삶도 그만큼 나아진다고 볼 수 있을까요?",
        "opt": ["A: 그렇다. 생산이 늘면 소득도 늘고 결국 삶이 나아진다",
                "B: 아니다. 가사노동·환경·분배는 GDP에 잡히지 않는다"]}
],
  4: [# 1. 밸런스 게임: 명목금리 vs 실질금리
    # [의미] 물가가 오르면 화폐 구매력이 감소하므로,
    #        저축·투자 의사결정에는 명목금리보다 실질금리가 적합함 (강의안 19p)
    {   "type": "balance", "id": 112,
        "q": "예금 상품을 고를 때 당신이 실제로 확인하는 것은?",
        "opt": ["A: 통장에 찍히는 숫자, 즉 은행이 제시한 금리(명목금리)",
                "B: 물가상승률을 뺀 실제 구매력 증가분(실질금리)"]},

    # 2. 퀴즈: PPI가 CPI보다 변동이 심한 이유
    # [정답] 원재료·중간재·자본재가 포함되기 때문
    # [근거] CPI는 소비재만, PPI는 원재료·중간재·자본재까지 포함 (강의안 27p)
    {   "type": "quiz", "id": 113,
        "q": "생산자물가지수(PPI)가 소비자물가지수(CPI)보다 변동이 심한 이유는?",
        "opt": ["조사 품목 수가 적기 때문",
                "가격변동이 심한 원재료·중간재·자본재가 포함되기 때문",
                "기준연도가 다르기 때문",
                "가중치를 쓰지 않기 때문"],
        "ans": "가격변동이 심한 원재료·중간재·자본재가 포함되기 때문"},

    # 3. 밸런스 게임: 환율 상승, 누구의 이야기인가
    # [의미] 같은 환율 상승이 수출기업 주주에게는 호재,
    #        해외여행자·유학생 학부모에게는 부담. 지표는 입장에 따라 다르게 읽힘.
    {   "type": "balance", "id": 114,
        "q": "환율이 1,400원을 넘었습니다. 당신에게 먼저 와닿는 것은?",
        "opt": ["A: 수출기업 실적이 좋아지겠네 (투자 기회)",
                "B: 이번 여름 해외여행은 접어야겠네 (비용 부담)"]}

]


    }


# =====================================================================
# [교수님 수정 구간 ②-C] 소비자재무설계2 문제은행  (item id: 201 ~ 299)
# =====================================================================

def get_cfp2_data():
    return {
        # 2: [
        #     {   "type": "balance", "id": 201,
        #         "q": "여기에 밸런스 게임 질문을 적으세요",
        #         "opt": ["A: 첫 번째 선택지", "B: 두 번째 선택지"]},
        # ],
    }


def get_lecture_bank():
    """과목 이름 → 그 과목의 주차별 문제 딕셔너리"""
    return {
        "재무설계1":       get_cfp1_data(),
        "가계자산투자설계": get_invest_data(),
        "재무설계2":       get_cfp2_data(),
    }


def get_week_items(class_name, week_no):
    """수업 이름 + 주차 → 해당 문제 리스트 (없으면 빈 리스트)"""
    course = CLASS_COURSE.get(class_name)
    return get_lecture_bank().get(course, {}).get(week_no, [])


# ---------------------------------------------------------------------
# 수파베이스 연결
# ---------------------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)


def load_active(class_name):
    """해당 수업의 현재 진행 상태 1건을 가져옵니다."""
    res = supabase.table("active_session").select("*").eq("class_name", class_name).execute()
    return res.data[0] if res.data else None


# ---------------------------------------------------------------------
# 세션 스테이트 초기화 (QR 주소에 ?class=...&name=...&id=... 로 전달 가능)
# ---------------------------------------------------------------------
if "std_name" not in st.session_state:
    st.session_state.std_name = st.query_params.get("name", "")
if "std_id" not in st.session_state:
    st.session_state.std_id = st.query_params.get("id", "")
if "std_class" not in st.session_state:
    qp_class = st.query_params.get("class", "")
    st.session_state.std_class = qp_class if qp_class in CLASS_LIST else ""


# ---------------------------------------------------------------------
# 사이드바
# ---------------------------------------------------------------------
is_admin = False
sel_class = None
sel_week = None

with st.sidebar:
    mode = st.radio("모드 선택", ["학생 참여", "교수 관리"])

    if mode == "교수 관리":
        pw = st.text_input("교수 비밀번호", type="password")
        if pw == "3383":
            is_admin = True
            st.success("관리자 모드 활성화")

            sel_class = st.selectbox("수업 선택", CLASS_LIST)
            sel_week = st.number_input("진행 주차", min_value=1, max_value=16, value=2)

            st.caption(f"문제은행: **{CLASS_COURSE[sel_class]}**")

            current_week_data = get_week_items(sel_class, sel_week)

            if not current_week_data:
                st.warning(f"⚠️ [{CLASS_COURSE[sel_class]}] {sel_week}주차 데이터가 코드에 등록되지 않았습니다.")
            else:
                active_row = load_active(sel_class)
                stored_idx = active_row["current_item_idx"] if active_row else 0

                if len(current_week_data) > 1:
                    new_idx = st.select_slider(
                        "문제 진행 상황",
                        options=range(len(current_week_data)),
                        value=min(stored_idx, len(current_week_data) - 1),
                        format_func=lambda x: f"{x+1}번 문제"
                    )
                else:
                    st.info("문제가 1개 등록되어 있습니다.")
                    new_idx = 0

                if st.button("📢 이 설정으로 수업 시작"):
                    supabase.table("active_session").upsert({
                        "class_name": sel_class,
                        "week_no": int(sel_week),
                        "current_item_idx": int(new_idx)
                    }, on_conflict="class_name").execute()
                    st.success(f"[{sel_class}] {sel_week}주차 {new_idx+1}번 문제로 세팅되었습니다.")
                    st.rerun()
        elif pw:
            st.error("비밀번호가 올바르지 않습니다.")


# =====================================================================
# 학생 참여 화면
# =====================================================================
if mode == "학생 참여":

    if not st.session_state.std_name or not st.session_state.std_id or not st.session_state.std_class:
        st.header("👋 반갑습니다! 정보를 입력해주세요.")

        default_idx = CLASS_LIST.index(st.session_state.std_class) if st.session_state.std_class in CLASS_LIST else 0
        in_class = st.selectbox("수강 중인 수업", CLASS_LIST, index=default_idx)

        col1, col2 = st.columns(2)
        in_name = col1.text_input("이름", value=st.session_state.std_name)
        in_id = col2.text_input("학번", value=st.session_state.std_id)

        if st.button("수업 참여하기"):
            if in_name and in_id:
                st.session_state.std_name = in_name
                st.session_state.std_id = in_id
                st.session_state.std_class = in_class
                st.rerun()
            else:
                st.error("이름과 학번을 모두 입력해주세요.")

    else:
        curr_class = st.session_state.std_class
        active_row = load_active(curr_class)

        if not active_row:
            st.warning(f"[{curr_class}] 교수님의 시작 버튼을 기다려주세요.")
        else:
            curr_week = active_row["week_no"]
            curr_idx = active_row["current_item_idx"]
            week_data = get_week_items(curr_class, curr_week)

            if not week_data:
                st.error(f"{curr_week}주차 강의 데이터가 준비되지 않았습니다.")
            elif curr_idx >= len(week_data):
                st.warning("교수님이 문제를 준비 중입니다. 잠시만 기다려주세요.")
            else:
                item = week_data[curr_idx]
                st.info(f"🎓 {st.session_state.std_name}님 | {curr_class} {curr_week}주차 진행 중")

                # 중복 제출 확인
                check = supabase.table("responses").select("*")\
                    .eq("std_id", st.session_state.std_id)\
                    .eq("class_name", curr_class)\
                    .eq("week_no", curr_week)\
                    .eq("item_id", item["id"]).execute()

                st.divider()

                if len(check.data) > 0:
                    st.warning(f"✅ 제출 완료: {item.get('q', item.get('title'))}")
                    if st.button("🔄 다음 문제 확인 (교수님이 안내하면 누르세요)"):
                        st.rerun()
                else:
                    base_row = {
                        "class_name": curr_class,
                        "week_no": curr_week,
                        "std_id": st.session_state.std_id,
                        "std_name": st.session_state.std_name,
                        "item_id": item["id"],
                    }

                    with st.form(f"live_form_{curr_class}_{curr_week}_{curr_idx}"):
                        st.markdown(f"### Q. {item.get('q', item.get('title'))}")

                        if item["type"] == "qr_survey":
                            a1 = st.radio(item["questions"][0]["q"], item["questions"][0]["opt"])
                            a2 = st.radio(item["questions"][1]["q"], item["questions"][1]["opt"])
                            if st.form_submit_button("유형 분석 제출"):
                                res = f"{'좋음' if '좋은' in a1 else '나쁨'}/{'만족' if '만족' in a2 else '불만족'}"
                                supabase.table("responses").insert(
                                    {**base_row, "item_type": "qr_survey", "response": res, "score": 1.0}
                                ).execute()
                                st.rerun()

                        elif item["type"] == "balance":
                            ans = st.radio("선택해주세요", item["opt"])
                            if st.form_submit_button("참여하기"):
                                supabase.table("responses").insert(
                                    {**base_row, "item_type": "balance", "response": ans, "score": 1.0}
                                ).execute()
                                st.rerun()

                        elif item["type"] == "quiz":
                            ans = st.radio("정답은?", item["opt"])
                            if st.form_submit_button("정답 제출"):
                                score = 1.0 if ans == item["ans"] else 0.5
                                supabase.table("responses").insert(
                                    {**base_row, "item_type": "quiz", "response": ans, "score": score}
                                ).execute()
                                st.rerun()


# =====================================================================
# 교수용 결과 모니터링
# =====================================================================
if mode == "교수 관리" and is_admin:
    st.divider()
    st.subheader(f"📊 {sel_class} {sel_week}주차 실시간 통계")

    res = supabase.table("responses").select("*")\
        .eq("class_name", sel_class).eq("week_no", int(sel_week)).limit(5000).execute()
    df = pd.DataFrame(res.data)

    if df.empty:
        st.info("아직 제출된 응답이 없습니다.")
    else:
        current_week_data = get_week_items(sel_class, sel_week)
        if current_week_data:
            active_row = load_active(sel_class)
            curr_idx = active_row["current_item_idx"] if active_row else 0
            curr_idx = min(curr_idx, len(current_week_data) - 1)
            curr_item = current_week_data[curr_idx]
            curr_df = df[df["item_id"] == curr_item["id"]]

            st.caption(f"현재 문제: {curr_idx+1}번 · {curr_item.get('q', curr_item.get('title'))}")

            if curr_df.empty:
                st.info("현재 문제에 대한 응답을 기다리는 중입니다.")
            else:
                st.metric("참여 인원", f"{len(curr_df)}명")
                chart_data = curr_df["response"].value_counts().reset_index()
                chart_data.columns = ["응답내용", "인원수"]
                chart = alt.Chart(chart_data).mark_bar(color="#E63946", size=50).encode(
                    x=alt.X("응답내용:N", title="응답 선택지"),
                    y=alt.Y("인원수:Q", title="인원수(명)")
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)

                if curr_item["type"] == "quiz":
                    correct = (curr_df["response"] == curr_item["ans"]).sum()
                    st.success(f"정답률: {correct}/{len(curr_df)}명 ({correct/len(curr_df)*100:.0f}%) · 정답: {curr_item['ans']}")

        with st.expander("🎓 학생별 이번 주 참여 점수 확인"):
            summary = df.groupby(["std_id", "std_name"])["score"].sum().reset_index()
            st.dataframe(summary.sort_values(by="score", ascending=False), use_container_width=True)
