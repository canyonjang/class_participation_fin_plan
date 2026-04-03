import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# --- [교수님 수정 구간: 주차별 데이터 관리] ---
@st.cache_data
def get_all_lecture_data():
    """
    주차를 키(Key)로 하고, 해당 주차의 문제 리스트를 값(Value)으로 갖는 딕셔너리입니다.
    새로운 주차 수업을 준비하실 때 아래 형식에 맞춰 추가만 하시면 됩니다.
    """
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
    # [근거] 어마어마한 수익률보다 '오랫동안 괜찮은 수준'을 유지하는 것이 복리의 핵심 [cite: 503]
    {   "type": "balance", "id": 16, 
        "q": "당신이 추구하는 투자 스타일은?", 
        "opt": ["A: 단기간에 엄청난 수익률을 내고 졸업하기", "B: 적당한 수익률이라도 수십 년간 꾸준히 유지하기"]},
    # 2. 밸런스 게임: 소비 부자 vs 자산 부자 (강의안 6p)
    # [근거] 부(Wealth)는 쓰지 않은 소득이며, 나중에 무언가를 사기 위한 선택권임 [cite: 504-508]
    {   "type": "balance", "id": 17, 
        "q": "당신이 더 꿈꾸는 부자의 모습은?", 
        "opt": ["A: 좋은 차와 집으로 부를 과시하는 '소비 부자'", "B: 겉은 검소하지만 언제든 쓸 수 있는 선택권을 가진 '자산 부자'"]},
    # 3. 퀴즈: 저축의 심리적 정의 (강의안 8p)
    # [근거] 저축 = 소득 - 자존심. 겸손을 늘리는 것이 저축의 핵심 [cite: 526-527]
    {   "type": "quiz", "id": 18, 
        "q": "모건 하우절이 정의한 '저축'의 공식으로 옳은 것은?", 
        "opt": ["저축 = 소득 - 소비", "저축 = 소득 - 자존심", "저축 = 투자수익 - 소비", "저축 = 소득 - 생활비"], 
        "ans": "저축 = 소득 - 자존심"},
    # 4. 퀴즈: 매몰 비용의 함정 (강의안 11p)
    # [근거] 과거의 노력에 얽매이지 말고, 상황이 변하면 계획을 가차 없이 버려야 함 [cite: 551-553]
    {   "type": "quiz", "id": 19, 
        "q": "과거의 노력에 얽매여 잘못된 의사결정을 하게 만드는 '사악한 역할'을 하는 비용은?", 
        "opt": ["기회 비용", "고정 비용", "매몰 비용", "가변 비용"], 
        "ans": "매몰 비용"},
    # 5. 밸런스 게임: 투자의 대가 - 입장료 vs 벌금 (강의안 12-17p)
    # [근거] 변동성과 불확실성은 투자의 성공을 위한 '입장료'임 [cite: 616-619]
    {   "type": "balance", "id": 20, 
        "q": "주가 폭락으로 내 자산이 하락했을 때, 당신의 생각은?", 
        "opt": ["A: 내가 뭔가 잘못한 것에 대한 '벌금'을 내고 있다", "B: 미래의 높은 수익을 얻기 위한 '입장료'를 내고 있다"]},
    # 6. 밸런스 게임: 나만의 게임 (강의안 18-19p)
    # [근거] 나와 다른 게임을 하는 사람들의 행동에 설득당하지 않는 것이 중요함 [cite: 633]
    {   "type": "balance", "id": 21, 
        "q": "주변 사람들이 단기 투자로 대박이 났다는 소문을 들었을 때?", 
        "opt": ["A: 나도 소외되지 않게 투자 방식을 바꾼다", "B: 그들과 나는 '다른 게임'을 하고 있음을 인정하고 내 길을 간다"]},
    # 7. 퀴즈: 자기과신의 특성 (강의안 20p)
    # [근거] 범위를 좁게 설정할수록(확신이 클수록) 자기과신 성향이 강함 [cite: 640-642]
    {   "type": "quiz", "id": 22, 
        "q": "자기과신(Overconfidence) 성향이 강한 사람의 특징으로 옳은 것은?", 
        "opt": ["자신의 실수를 잘 예측한다", "정답의 범위를 아주 넓게 설정한다", "자신의 예측 범위에 대한 확신이 커서 범위를 좁게 잡는다", "전문가의 조언을 맹신한다"], 
        "ans": "자신의 예측 범위에 대한 확신이 커서 범위를 좁게 잡는다"}
],
   6: [   
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
]

        
    }

# 전체 데이터 로드
all_lecture_data = get_all_lecture_data()

# 수파베이스 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="소비자재무설계 라이브 참여", layout="wide")

# 세션 스테이트 초기화
if "std_name" not in st.session_state:
    st.session_state.std_name = st.query_params.get("name", "")
if "std_id" not in st.session_state:
    st.session_state.std_id = st.query_params.get("id", "")

# 사이드바 설정
with st.sidebar:
    mode = st.radio("모드 선택", ["학생 참여", "교수 관리"])
    if mode == "교수 관리":
        pw = st.text_input("교수 비밀번호", type="password")
        if pw == "3383":
            st.success("관리자 모드 활성화")
            sel_class = st.selectbox("수업 선택", ["인하대 소비자재무설계", "숙대 소비자재무설계1_001", "숙대 소비자재무설계1_002"])
            sel_week = st.number_input("진행 주차", min_value=1, max_value=14, value=2)
            
            # 선택한 주차의 문제 리스트 가져오기
            current_week_data = all_lecture_data.get(sel_week, [])
            
            if not current_week_data:
                st.warning(f"⚠️ {sel_week}주차 데이터가 코드에 등록되지 않았습니다.")
            else:
                # 수파베이스에서 기존 진행 정보 가져오기
                active_data = supabase.table("active_session").select("*").eq("id", 1).execute()
                stored_idx = active_data.data[0]['current_item_idx'] if active_data.data else 0
                
                # [수정 포인트] 문제가 2개 이상일 때만 슬라이더 표시
                if len(current_week_data) > 1:
                    new_idx = st.select_slider(
                        "문제 진행 상황", 
                        options=range(len(current_week_data)), 
                        value=min(stored_idx, len(current_week_data)-1),
                        format_func=lambda x: f"{x+1}번 문제"
                    )
                else:
                    # 문제가 1개인 경우 슬라이더 없이 0번 인덱스 고정
                    st.info("문제가 1개 등록되어 있습니다.")
                    new_idx = 0
                
                if st.button("📢 이 설정으로 수업 시작"):
                    supabase.table("active_session").upsert({
                        "id": 1, "class_name": sel_class, "week_no": sel_week, "current_item_idx": new_idx
                    }).execute()
                    st.success(f"{sel_week}주차 {new_idx+1}번 문제로 세팅되었습니다.")
                    st.rerun()

# --- 학생 참여 화면 ---
if mode == "학생 참여":
    if not st.session_state.std_name or not st.session_state.std_id:
        st.header("👋 반갑습니다! 정보를 입력해주세요.")
        col1, col2 = st.columns(2)
        in_name = col1.text_input("이름")
        in_id = col2.text_input("학번")
        
        if st.button("수업 참여하기"):
            if in_name and in_id:
                st.session_state.std_name, st.session_state.std_id = in_name, in_id
                st.rerun()
    else:
        # 현재 활성화된 세션 정보 가져오기
        active = supabase.table("active_session").select("*").eq("id", 1).execute()
        if active.data:
            curr_class = active.data[0]['class_name']
            curr_week = active.data[0]['week_no']
            curr_idx = active.data[0]['current_item_idx']
            
            # 현재 주차에 맞는 데이터 셋 선택
            week_data = all_lecture_data.get(curr_week, [])
            
            if not week_data:
                st.error(f"{curr_week}주차 강의 데이터가 준비되지 않았습니다.")
            else:
                item = week_data[curr_idx]
                st.info(f"🎓 {st.session_state.std_name}님 | {curr_class} {curr_week}주차 진행 중")
                
                # 중복 제출 확인
                check = supabase.table("responses").select("*")\
                    .eq("std_id", st.session_state.std_id)\
                    .eq("class_name", curr_class)\
                    .eq("week_no", curr_week)\
                    .eq("item_id", item['id']).execute()

                st.divider()
                
                if len(check.data) > 0:
                    st.warning(f"✅ 제출 완료: {item.get('q', item.get('title'))}")
                    if st.button("🔄 다음 문제 확인 (교수님이 안내하면 누르세요)"):
                        st.rerun()
                else:
                    with st.form(f"live_form_{curr_week}_{curr_idx}"):
                        st.markdown(f"### Q. {item.get('q', item.get('title'))}")
                        
                        if item['type'] == "qr_survey":
                            a1 = st.radio(item['questions'][0]['q'], item['questions'][0]['opt'])
                            a2 = st.radio(item['questions'][1]['q'], item['questions'][1]['opt'])
                            if st.form_submit_button("유형 분석 제출"):
                                res = f"{'좋음' if '좋은' in a1 else '나쁨'}/{'만족' if '만족' in a2 else '불만족'}"
                                supabase.table("responses").insert({"class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name, "item_id": item['id'], "item_type": "qr_survey", "response": res, "score": 1.0}).execute()
                                st.rerun()

                        elif item['type'] == "balance":
                            ans = st.radio("선택해주세요", item['opt'])
                            if st.form_submit_button("참여하기"):
                                supabase.table("responses").insert({"class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name, "item_id": item['id'], "item_type": "balance", "response": ans, "score": 1.0}).execute()
                                st.rerun()

                        elif item['type'] == "quiz":
                            ans = st.radio("정답은?", item['opt'])
                            if st.form_submit_button("정답 제출"):
                                score = 1.0 if ans == item['ans'] else 0.5
                                supabase.table("responses").insert({"class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name, "item_id": item['id'], "item_type": "quiz", "response": ans, "score": score}).execute()
                                st.rerun()
        else:
            st.warning("교수님의 시작 버튼을 기다려주세요.")

# --- 교수용 결과 모니터링 (선택한 주차 기준) ---
if mode == "교수 관리" and pw == "3383":
    st.divider()
    st.subheader(f"📊 {sel_class} {sel_week}주차 실시간 통계")
    res = supabase.table("responses").select("*").eq("class_name", sel_class).eq("week_no", sel_week).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        # 현재 활성화된 문제에 대한 통계만 표시
        current_week_data = all_lecture_data.get(sel_week, [])
        if current_week_data:
            active_session = supabase.table("active_session").select("*").eq("id", 1).execute()
            curr_idx = active_session.data[0]['current_item_idx'] if active_session.data else 0
            curr_item_id = current_week_data[curr_idx]['id']
            curr_df = df[df['item_id'] == curr_item_id]
         
            if not curr_df.empty:
                chart_data = curr_df['response'].value_counts().reset_index()
                chart_data.columns = ['응답내용', '인원수']
                chart = alt.Chart(chart_data).mark_bar(color='#E63946', size=50).encode(
                    x=alt.X('응답내용:N', title='응답 선택지'),
                    y=alt.Y('인원수:Q', title='인원수(명)')
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
            
            with st.expander("🎓 학생별 이번 주 참여 점수 확인"):
                summary = df.groupby(['std_id', 'std_name'])['score'].sum().reset_index()
                st.dataframe(summary.sort_values(by='score', ascending=False), use_container_width=True)



