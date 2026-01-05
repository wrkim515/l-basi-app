import streamlit as st

# --- 1. L-BASI 로직 (두뇌) ---
def analyze_l_basi(products_text, symptom_level):
    # 1-1. 제품 분류 키워드
    triggers_keywords = ["레티놀", "비타민C", "아하", "바하", "AHA", "BHA", "필링", "스크럽", "미백", "주름", "고기능", "애시드", "L-AA"]
    primers_keywords = ["토너", "스킨", "로션", "세라마이드", "장벽", "보습", "수분", "히알루론산", "크림", "에센스"]
    stabilizers_keywords = ["시카", "진정", "재생", "판테놀", "마데카", "리페어", "오일", "밤", "병풀", "알로에"]

    my_routine = {"Primer": [], "Trigger": [], "Stabilizer": [], "Unknown": []}
    
    # 1-2. 입력된 텍스트를 줄바꿈 기준으로 나누기
    product_list = [p.strip() for p in products_text.split('\n') if p.strip()]

    # 1-3. 제품 분류 실행
    for product in product_list:
        classified = False
        # Trigger 분류 우선
        for key in triggers_keywords:
            if key in product:
                my_routine["Trigger"].append(product)
                classified = True
                break
        if not classified:
            for key in stabilizers_keywords:
                if key in product:
                    my_routine["Stabilizer"].append(product)
                    classified = True
                    break
        if not classified:
            for key in primers_keywords:
                if key in product:
                    my_routine["Primer"].append(product)
                    classified = True
                    break
        if not classified:
            my_routine["Unknown"].append(product)

    # 1-4. 5단계 강도에 따른 조언 (핵심 로직 변경!)
    advice = ""
    status = "Normal"

    if symptom_level == 1: # 없음
        status = "Normal"
        advice = """
        ✅ **최적의 상태(Stable)입니다.**
        
        피부가 아주 편안하네요! 현재 루틴을 유지하시고, **Trigger(기능성) 제품**을 적극적으로 써서 효과를 보세요.
        """
        
    elif symptom_level == 2: # 미약함
        status = "Caution"
        advice = """
        🙂 **괜찮은 상태(Acceptable)입니다.**
        
        약간 느낌은 있지만 계속 쓸 수 있어요. 단, **Trigger 제품 양을 반으로** 줄이거나, 이틀에 한 번만 쓰세요.
        """
        
    elif symptom_level == 3: # 거슬림 -> 여기서부터 Trigger 중단!
        status = "Warning"
        advice = """
        ✋ **주의(Caution) 단계입니다. Trigger를 멈추세요.**
        
        불편한 게 신경 쓰이기 시작했네요. 욕심내지 마세요.
        **Trigger(기능성) 사용을 멈추고**, Primer(장벽) 바르는 것에만 집중하세요.
        """
        
    elif symptom_level == 4: # 심함
        status = "Danger"
        advice = """
        🚨 **위험(Danger) 단계입니다. 즉시 중단하세요!**
        
        피부 장벽이 다쳤습니다. 
        모든 기능성 제품을 끊고, 순한 세안제와 **진정 크림(Stabilizer)**만 쓰세요.
        """
        
    elif symptom_level == 5: # 매우 심함
        status = "Medical"
        advice = """
        🏥 **병원에 가야 할 상태(Medical)입니다.**
        
        화장품으로 해결할 수 없습니다.
        아무것도 바르지 말고 **피부과 의사 선생님**을 만나보세요.
        """

    return my_routine, status, advice

# --- 2. 웹사이트 화면 꾸미기 ---
st.set_page_config(page_title="L-BASI Skin OS", page_icon="🧬")

st.title("🧬 L-BASI™ Skin OS")
st.markdown("### 화장품 사용 순서 최적화 가이드 (v2.0)")
st.info("💡 5단계 자가 진단을 통해 '지금 발라도 되는지'를 판단해 드립니다.")

st.divider()

# [질문 1] 5단계 증상 선택 (라디오 버튼으로 변경!)
st.subheader("1. 현재 피부 상태를 골라주세요")
st.caption("가장 비슷한 문장을 하나만 선택하세요.")

symptom_options = [
    (1, "😄 1단계: 없음 (아주 편안해요)"),
    (2, "🙂 2단계: 미약함 (바를 때만 살짝 따끔하고 금방 사라져요)"),
    (3, "😐 3단계: 거슬림 (화끈거림이나 붉은 기가 10분 이상 가요)"),
    (4, "😣 4단계: 심함 (참기 힘들 정도로 따갑거나 아파요)"),
    (5, "😱 5단계: 매우 심함 (진물이 나거나 심하게 부어올랐어요)")
]

# 사용자가 선택한 옵션 저장
selected_option = st.radio(
    "증상 강도:",
    symptom_options,
    format_func=lambda x: x[1] # 화면에는 글자만 보여줌
)
selected_level = selected_option[0] # 선택된 숫자 (1~5)

# [질문 2] 화장품 목록 입력
st.divider()
st.subheader("2. 가지고 있는 기초 화장품 이름을 적어주세요")
st.caption("제품명을 한 줄에 하나씩 입력하세요. (예: 이니스프리 레티놀 앰플)")
products_input = st.text_area("화장품 목록 입력", height=150, placeholder="여기에 입력하세요...")

# 버튼
if st.button("내 루틴 진단하기 🔍", type="primary"):
    if not products_input:
        st.error("화장품 목록을 입력해주세요!")
    else:
        # 분석 시작
        routine, status, advice_text = analyze_l_basi(products_input, selected_level)

        st.divider()
        st.header("📊 L-BASI 분석 결과")

        # 1. 진단 결과 메시지 (색상 구분)
        if status == "Normal":
            st.success(advice_text)
        elif status == "Caution":
            st.info(advice_text)
        elif status == "Warning":
            st.warning(advice_text)
        elif status == "Danger":
            st.error(advice_text)
        elif status == "Medical":
            st.error(advice_text)

        # 2. 제품 재배치 시각화
        st.subheader("🧴 당신의 화장품 재배치")
        
        col1, col2, col3 = st.columns(3)

        # 3단계 이상(Warning~)부터는 Trigger 사용 금지 표시!
        stop_trigger = selected_level >= 3 

        with col1:
            st.markdown("**1. Primer (환경조성)**")
            if routine["Primer"]:
                for p in routine["Primer"]:
                    st.success(f"Op: {p}")
            else:
                st.caption("없음")

        with col2:
            st.markdown("**2. Trigger (기능활성)**")
            if routine["Trigger"]:
                for p in routine["Trigger"]:
                    if stop_trigger:
                        # 3단계 이상이면 빨간색 취소선
                        st.error(f"⛔ ~~{p}~~ (중단)")
                    elif selected_level == 2:
                        # 2단계면 주의 표시
                        st.warning(f"⚠️ {p} (양 줄이기)")
                    else:
                        # 1단계면 정상
                        st.warning(f"⚡ {p}")
            else:
                st.caption("없음")

        with col3:
            st.markdown("**3. Stabilizer (안정화)**")
            if routine["Stabilizer"]:
                for p in routine["Stabilizer"]:
                    st.info(f"🛡️ {p}")
            else:
                st.caption("없음")

        if routine["Unknown"]:
            st.caption(f"※ 분류 불가: {', '.join(routine['Unknown'])}")
