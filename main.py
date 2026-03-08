import streamlit as st
from supabase import create_client
import pandas as pd
import pytz
from datetime import datetime

# --- [교수님 수정 구간: 강의 내용 및 순서] ---
# 여기서 리스트의 순서를 바꾸거나 내용을 수정하면 웹앱에 즉시 반영됩니다.
lecture_data = [
    # 1. QR 설문: 경제적 복지 유형 (11-16p)
    {
        "type": "qr_survey", "id": 1, "title": "나의 경제적 복지 유형 파악",
        "questions": [
            {"q": "객관적으로 판단할 때, 나의 소득과 소비생활 수준은?", "opt": ["매우 나쁜 상황이다", "나쁜 상황이다", "좋은 상황이다", "매우 좋은 상황이다"]},
            {"q": "주관적으로 생각하면, 나의 소득과 소비생활 수준은?", "opt": ["매우 불만족스럽다", "불만족스럽다", "만족스럽다", "매우 만족스럽다"]}
        ]
    },
    # 2. 밸런스 게임: 객관적 풍요 vs 주관적 만족 (14p)
    {"type": "balance", "id": 2, "q": "더 선호하는 삶의 형태는?", "opt": ["A: 돈은 평균 이상이나 늘 불만족한 삶", "B: 자산은 부족해도 스스로 만족하는 삶"]},
    # 3. 밸런스 게임: 돈으로 인한 변화 (26p)
    {"type": "balance", "id": 3, "q": "로또 당첨 시 더 기대되는 변화는?", "opt": ["A: 소비행태, 자동차 등 외적인 변화", "B: 목표, 가치관 등 내적인 변화"]},
    # 4. 밸런스 게임: 금융사회화의 원천 (29-30p)
    {"type": "balance", "id": 4, "q": "누구의 조언을 더 신뢰하시나요?", "opt": ["A: 저축을 강조하는 부모님의 경험", "B: 투자 방법을 알려주는 유튜브 및 경제신문의 정보"]},
    # 5. 밸런스 게임: 재무적 부정직 (33p)
    {"type": "balance", "id": 5, "q": "더 화나는 배우자의 비밀은?", "opt": ["A: 나 몰래 자기 부모님 용돈 드리기", "B: 나 몰래 비상금으로 주식 투자하기"]},
    # 6. 퀴즈: 메달리스트 행복 (34p)
    {"type": "quiz", "id": 6, "q": "동메달(7.1점)이 은메달(4.8점)보다 행복한 이유는?", "opt": ["상향 비교", "하향 비교", "절대적 만족"], "ans": "하향 비교"},
    # 7. 밸런스 게임: 남과의 비교 (35p)
    {"type": "balance", "id": 7, "q": "더 불행한 상황은?", "opt": ["A: 나는 20% 수익을 냈는데, 가장 친한 친구는 100% 수익(대박)을 냄", "B: 나는 10% 손실을 봤는데, 주변 사람들은 모두 나보다 더 큰 손실을 봄"]},
    # 8. 퀴즈: 재무 불안 지표 (38-39p)
    {"type": "quiz", "id": 8, "q": "조사 결과 가장 낮은 점수를 기록한 불안 영역은?", "opt": ["필수지출 불안", "재정안정성 불안", "부채 불안"], "ans": "필수지출 불안"},
    # 9. 퀴즈: 재무 스트레스 (41p)
    {"type": "quiz", "id": 9, "q": "주부들이 지출 스트레스보다 더 강하게 느끼는 것은?", "opt": ["소득 스트레스", "자산 스트레스", "부채 스트레스"], "ans": "자산 스트레스"}
]
# --------------------------------------------

# 수파베이스 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="소비자재무설계 라이브 참여", layout="wide")

# --- 쿼리 파라미터 기반 정보 복구 로직 ---
# 주소창에 이름/학번 정보가 있다면 세션에 자동으로 채워줍니다.
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
            
            active_data = supabase.table("active_session").select("*").eq("id", 1).execute()
            idx = active_data.data[0]['current_item_idx'] if active_data.data else 0
            
            new_idx = st.select_slider("문제 진행 상황", options=range(len(lecture_data)), value=idx)
            if st.button("📢 이 수업/문제로 전체 시작"):
                supabase.table("active_session").upsert({
                    "id": 1, "class_name": sel_class, "week_no": sel_week, "current_item_idx": new_idx
                }).execute()
                st.rerun()

# --- 학생 참여 화면 ---
if mode == "학생 참여":
    # 이름이나 학번이 주소창/세션에 모두 없으면 입력창 표시
    if not st.session_state.std_name or not st.session_state.std_id:
        st.header("👋 반갑습니다! 정보를 입력해주세요.")
        col1, col2 = st.columns(2)
        in_name = col1.text_input("이름")
        in_id = col2.text_input("학번")
        
        if st.button("수업 참여하기"):
            if in_name and in_id:
                # 1. 세션에 저장
                st.session_state.std_name = in_name
                st.session_state.std_id = in_id
                # 2. 주소창(URL)에 저장 (새로고침 대비)
                st.query_params["name"] = in_name
                st.query_params["id"] = in_id
                st.rerun()
            else:
                st.error("이름과 학번을 모두 입력해주세요.")
    
    # 정보가 있는 경우 (정상 참여 상태)
    else:
        active = supabase.table("active_session").select("*").eq("id", 1).execute()
        
        if active.data:
            curr_class = active.data[0]['class_name']
            curr_week = active.data[0]['week_no']
            curr_idx = active.data[0]['current_item_idx']
            item = lecture_data[curr_idx]
            
            st.info(f"🎓 {st.session_state.std_name}({st.session_state.std_id})님 환영합니다! | {curr_class} {curr_week}주차")
            if st.button("정보 수정 (로그아웃)"):
                st.session_state.std_name = ""
                st.session_state.std_id = ""
                st.query_params.clear() # 주소창 정보도 삭제
                st.rerun()

            st.divider()
            # 새로고침 없이도 교수님이 넘긴 정보를 반영하기 위한 버튼
            if st.button("🔄 다음 문제 확인 (수동 새로고침)"):
                st.rerun()

            with st.form(f"live_form_{curr_idx}"):
                st.markdown(f"### Q. {item.get('q', item.get('title'))}")
                
                if item['type'] == "qr_survey":
                    a1 = st.radio(item['questions'][0]['q'], item['questions'][0]['opt'])
                    a2 = st.radio(item['questions'][1]['q'], item['questions'][1]['opt'])
                    if st.form_submit_button("유형 분석 제출"):
                        res = f"{'좋음' if '좋은' in a1 else '나쁨'}/{'만족' if '만족' in a2 else '불만족'}"
                        supabase.table("responses").insert({
                            "class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name,
                            "item_id": item['id'], "item_type": "qr_survey", "response": res, "score": 1.0
                        }).execute()
                        st.balloons()
                        st.success(f"제출 완료! 당신의 유형: {res}")

                elif item['type'] == "balance":
                    ans = st.radio("선택해주세요", item['opt'])
                    if st.form_submit_button("참여하기"):
                        supabase.table("responses").insert({
                            "class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name,
                            "item_id": item['id'], "item_type": "balance", "response": ans, "score": 1.0
                        }).execute()
                        st.success("참여 점수가 기록되었습니다.")

                elif item['type'] == "quiz":
                    ans = st.radio("정답은?", item['opt'])
                    if st.form_submit_button("정답 제출"):
                        score = 1.0 if ans == item['ans'] else 0.5
                        supabase.table("responses").insert({
                            "class_name": curr_class, "week_no": curr_week, "std_id": st.session_state.std_id, "std_name": st.session_state.std_name,
                            "item_id": item['id'], "item_type": "quiz", "response": ans, "score": score
                        }).execute()
                        st.success("퀴즈 응답이 제출되었습니다!")
        else:
            st.warning("교수님의 시작 버튼을 기다려주세요.")

# --- 교수용 결과 모니터링 ---
if mode == "교수 관리" and pw == "3383":
    st.divider()
    st.subheader(f"📊 {sel_class} {sel_week}주차 실시간 통계")
    res = supabase.table("responses").select("*").eq("class_name", sel_class).eq("week_no", sel_week).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        curr_item_id = lecture_data[new_idx]['id']
        curr_df = df[df['item_id'] == curr_item_id]
        if not curr_df.empty:
            st.bar_chart(curr_df['response'].value_counts())
        
        with st.expander("🎓 학생별 누적 참여 점수 확인"):
            summary = df.groupby(['std_id', 'std_name'])['score'].sum().reset_index()
            st.dataframe(summary.sort_values(by='score', ascending=False))
