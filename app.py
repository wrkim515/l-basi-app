import streamlit as st

# --- 1. L-BASI 로직 (두뇌) ---
def analyze_l_basi(products_text, symptoms):
    # 1-1. 제품 분류 키워드
    triggers_keywords = ["레티놀", "비타민C", "아하", "바하", "AHA", "BHA", "필링", "스크럽", "미백", "주름", "고기능", "애시드"]
    primers_keywords = ["토너", "스킨", "로션", "세라마이드", "장벽", "보습", "수분", "히알루론산", "크림"]
    stabilizers_keywords = ["시카", "진정", "재생", "판테놀", "마데카", "리페어", "오일", "밤", "병풀"]

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

    # 1-4. 증상 기반 조언 (핵심 로직)
    advice = ""
    status = "Normal"

    if "따가움/화끈거림" in symptoms or "지속되는 붉은기" in symptoms:
        status = "Danger"
        advice = """
        🚨 **L-BASI 긴급 경고: Trigger(활성 성분) 사용을 즉시 중단하십시오.**
        
        현재 피부 방어선(Terrain)이 무너져 있습니다. 지금 고기능성 제품을 바르는 것은 피부를 공격하는 것입니다.
        모든 Trigger 제품을 빼고, **Primer(장벽)와 Stabilizer(진정)**에만 3~5일간 집중하세요.
        """
    elif "세안 후 심한 당김" in symptoms or "하얀 각질" in symptoms:
        status = "Caution"
        advice = """
        ⚠️ **Terrain(기초 환경) 보강이 필요합니다.**
        
        피부가 Trigger를 받아들일 준비가 덜 되었습니다. 
        Trigger 제품은 주 2회 이하로 줄이고, **Primer(수분/장벽) 단계**를 평소보다 꼼꼼히 바르세요.
        """
    else:
        status = "Normal"
        advice = """
        ✅ **피부 컨디션이 안정적입니다.**
        
        현재 루틴을 유지하셔도 좋습니다. 
        더 높은 효과를 원하신다면, **Trigger** 제품을 야간 루틴에 적극적으로 활용해보세요.
        """

    return my_routine, status, advice

# --- 2. 웹사이트 화면 꾸미기 ---
st.set_page_config(page_title="L-BASI Skin OS", page_icon="🧬")

st.title("🧬 L-BASI™ Skin OS")
st.markdown("### 화장품 사용 순서 최적화 가이드")
st.info("💡 이 서비스는 제품을 추천하는 것이 아니라, 가진 화장품을 **'지금 써도 되는지'** 판단해 드립니다.")

st.divider()

# [질문 1] 증상
st.subheader("1. 오늘 피부 상태는 어떤가요?")
symptoms = st.multiselect(
    "해당하는 것을 모두 골라주세요:",
    ["없음 (편안함)", "세안 후 심한 당김", "따가움/화끈거림", "지속되는 붉은기", "하얀 각질", "가려움"]
)

# [질문 2] 화장품 목록
st.subheader("2. 가지고 있는 기초 화장품 이름을 적어주세요")
st.caption("제품명을 한 줄에 하나씩 입력하세요. (예: 이니스프리 레티놀 앰플)")
products_input = st.text_area("화장품 목록 입력", height=150, placeholder="여기에 입력하세요...")

# 버튼
if st.button("내 루틴 진단하기 🔍", type="primary"):
    if not products_input:
        st.error("화장품 목록을 입력해주세요!")
    else:
        # 분석 시작
        routine, status, advice_text = analyze_l_basi(products_input, symptoms)

        st.divider()
        st.header("📊 L-BASI 분석 결과")

        # 결과 메시지
        if status == "Danger":
            st.error(advice_text)
        elif status == "Caution":
            st.warning(advice_text)
        else:
            st.success(advice_text)

        # 분류 결과 보여주기
        st.subheader("🧴 당신의 화장품 재배치")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**1. Primer (환경조성)**")
            for p in routine["Primer"]:
                st.success(f"Op: {p}")

        with col2:
            st.markdown("**2. Trigger (기능활성)**")
            for p in routine["Trigger"]:
                if status == "Danger":
                    st.error(f"⛔ ~~{p}~~ (중단)")
                else:
                    st.warning(f"⚡ {p}")

        with col3:
            st.markdown("**3. Stabilizer (안정화)**")
            for p in routine["Stabilizer"]:
                st.info(f"🛡️ {p}")

        if routine["Unknown"]:
            st.caption(f"※ 분류 불가: {', '.join(routine['Unknown'])}")
