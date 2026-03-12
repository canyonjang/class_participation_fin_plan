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
        3: [ # 3주차 수업 자료 (예시: 5개 추가 시 여기에 작성)
            {"type": "balance", "id": 10, "q": "3주차 첫 번째 질문 예시입니다.", "opt": ["선택지 A", "선택지 B"]},
            # 여기에 11, 12, 13, 14번을 이어서 작성하시면 됩니다.
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


