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

# 수파베이스 연결 설정
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="소비자재무설계 강의 참여", layout="wide")

# 사이드바 관리자 설정
with st.sidebar:
    mode = st.radio("모드 선택", ["학생 참여", "교수 관리"])
    if mode == "교수 관리":
        pw = st.text_input("교수 비밀번호", type="password")
        if pw == "3383":
            st.success("인증되었습니다.")
            sel_class = st.selectbox("수업 선택", ["인하대 소비자재무설계", "숙대 소비자재무설계1_001", "숙대 소비자재무설계1_002"])
            sel_week = st.number_input("수업 주차", min_value=1, max_value=14, value=2)
            
            # 현재 상태 제어
            status = supabase.table("class_status").select("*").eq("class_name", sel_class).execute()
            idx = status.data[0]['current_item_idx'] if status.data else 0
            
            new_idx = st.select_slider("문제 진행 상황", options=range(len(lecture_data)), value=idx)
            if st.button("📢 현재 문제로 시작"):
                supabase.table("class_status").upsert({"class_name": sel_class, "current_week": sel_week, "current_item_idx": new_idx}).execute()
                st.rerun()

# 학생 참여 화면
if mode == "학생 참여":
    st.header("📝 실시간 강의 참여")
    c1, c2 = st.columns(2)
    name = c1.text_input("이름")
    std_id = c2.text_input("학번")
    s_class = st.selectbox("수업 선택", ["인하대 소비자재무설계", "숙대 소비자재무설계1_001", "숙대 소비자재무설계1_002"])

    if name and std_id:
        status = supabase.table("class_status").select("*").eq("class_name", s_class).execute()
        if status.data:
            curr_idx = status.data[0]['current_item_idx']
            curr_week = status.data[0]['current_week']
            item = lecture_data[curr_idx]
            
            st.info(f"[{s_class}] {curr_week}주차 활동 진행 중")
            
            with st.form(f"form_{curr_idx}"):
                st.subheader(item.get("q", item.get("title")))
                
                if item['type'] == "qr_survey":
                    ans1 = st.radio(item['questions'][0]['q'], item['questions'][0]['opt'])
                    ans2 = st.radio(item['questions'][1]['q'], item['questions'][1]['opt'])
                    if st.form_submit_button("유형 분석 제출"):
                        obj = "좋음" if "좋은" in ans1 else "나쁨"
                        subj = "만족" if "만족" in ans2 else "불만족"
                        res = f"{obj}/{subj}"
                        supabase.table("responses").insert({"class_name": s_class, "week_no": curr_week, "std_id": std_id, "std_name": name, "item_id": item['id'], "item_type": "qr_survey", "response": res, "score": 1.0}).execute()
                        st.success(f"당신의 유형: {res} (판별 완료)")
                
                elif item['type'] == "balance":
                    ans = st.radio("당신의 선택은?", item['opt'])
                    if st.form_submit_button("응답 제출"):
                        supabase.table("responses").insert({"class_name": s_class, "week_no": curr_week, "std_id": std_id, "std_name": name, "item_id": item['id'], "item_type": "balance", "response": ans, "score": 1.0}).execute()
                        st.success("참여 점수 1점이 기록되었습니다!")

                elif item['type'] == "quiz":
                    ans = st.radio("정답을 고르세요", item['opt'])
                    if st.form_submit_button("정답 확인"):
                        is_correct = 1.5 if ans == item['ans'] else 0.5
                        supabase.table("responses").insert({"class_name": s_class, "week_no": curr_week, "std_id": std_id, "std_name": name, "item_id": item['id'], "item_type": "quiz", "response": ans, "score": is_correct}).execute()
                        st.success("제출 완료!")

# 관리자 실시간 통계 (비번 인증 시 하단 노출)
if mode == "교수 관리" and pw == "3383":
    st.divider()
    st.subheader(f"📊 {sel_class} {sel_week}주차 실시간 참여 통계")
    res = supabase.table("responses").select("*").eq("class_name", sel_class).eq("week_no", sel_week).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        curr_q = df[df['item_id'] == lecture_data[new_idx]['id']]
        if not curr_q.empty:
            st.bar_chart(curr_q['response'].value_counts())
        
        if st.checkbox("학생별 누적 참여 점수 확인"):
            summary = df.groupby(['std_id', 'std_name'])['score'].sum().reset_index()

            st.dataframe(summary.sort_values(by='score', ascending=False))
