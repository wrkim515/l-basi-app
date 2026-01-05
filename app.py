import streamlit as st
import re

# ==========================================
# 1. 핵심 로직 (두뇌)
# ==========================================

def classify_products(products_text):
    """
    입력된 화장품 텍스트를 분석하여 Primer, Trigger, Stabilizer로 분류하는 함수
    """
    # 키워드 데이터베이스 (필요시 계속 추가 가능)
    triggers_keywords = ["레티놀", "비타민C", "아하", "바하", "AHA", "BHA", "필링", "스크럽", "미백", "주름", "고기능", "애시드", "L-AA", "엔자임", "박피"]
    primers_keywords = ["토너", "스킨", "로션", "세라마이드", "장벽", "보습", "수분", "히알루론산", "크림", "에센스", "부스터", "프라이머"]
    stabilizers_keywords = ["시카", "진정", "재생", "판테놀", "마데카", "리페어", "오일", "밤", "병풀", "알로에", "쑥", "어성초"]

    my_routine = {"Primer": [], "Trigger": [], "Stabilizer": [], "Unknown": []}
    
    # 입력된 텍스트를 줄바꿈 기준으로 나누기
    product_list = [p.strip() for p in products_text.split('\n') if p.strip()]

    for product in product_list:
        classified = False
        # 1순위: Trigger (가장 중요하므로 먼저 분류)
        for key in triggers_keywords:
            if key in product:
                my_routine["Trigger"].append(product)
                classified = True
                break
        # 2순위: Stabilizer
        if not classified:
            for key in stabilizers_keywords:
                if key in product:
                    my_routine["Stabilizer"].append(product)
                    classified = True
                    break
        # 3순위: Primer
        if not classified:
            for key in primers_keywords:
                if key in product:
                    my_routine["Primer"].append(product)
                    classified = True
                    break
        # 미분류
        if not classified:
            my_routine["Unknown"].append(product)
            
    return my_routine

def calculate_status(score, is_procedure):
    """
    설문 점수와 시술 여부를 바탕으로 피부 상태(Status)를 판정하는 함수
    """
    # 시술 직후면 점수와 상관없이 최소 '경고' 단계 이상
    if is_procedure == "네":
        if score >= 10: return "Danger"
        return "Warning" 
    
    # 점수에 따른 상태 판정
    if score >= 10: return "Danger"
    elif score >= 6: return "Warning"
    elif score >= 3: return "Caution"
    else: return "Normal"

def get_advice_text(status):
    """
    상태에 따른 맞춤형 조언 텍스트 반환
    """
    if status == "Normal":
        return """
        ✅ **안정(Stable) 단계입니다.**
        
        피부 컨디션이 최적입니다! 현재 장벽이 튼튼하게 유지되고 있습니다.
        **Trigger(기능성) 제품**을 적극적으로 사용하여 피부 개선 효과를 극대화하세요.
        """
    elif status == "Caution":
        return """
        🙂 **주의(Caution)가 필요합니다.**
        
        피부 장벽이 살짝 약해져 있거나 미세한 자극이 있습니다.
        **Trigger 제품의 양을 평소의 절반**으로 줄이고, 수분 공급(Primer)에 더 신경 쓰세요.
        """
    elif status == "Warning":
        return """
        ✋ **경고(Warning) 단계입니다. Trigger를 멈추세요.**
        
        피부가 자극 신호를 보내고 있습니다. 욕심내지 마세요.
        **모든 Trigger(기능성) 사용을 일시 중단**하고, 장벽 복구(Primer)에만 집중할 때입니다.
        """
    elif status == "Danger":
        return """
        🚨 **위험(Danger) 단계입니다.**
        
        피부 방어선이 무너졌습니다. 지금 기능성 제품을 바르는 건 피부를 공격하는 것입니다.
        모든 화장품을 끊고, **순한 세안제와 진정 크림(Stabilizer)**만 사용하세요. 필요시 피부과 방문을 권장합니다.
        """
    return ""

def extract_score(text):
    """
    선택지 텍스트에서 점수만 쏙 뽑아내는 함수 (예: '아프다 (5점)' -> 5)
    """
    match = re.search(r'\((\d+)점\)', text)
    return int(match.group(1)) if match else 0


# ==========================================
# 2. 웹사이트 화면 구성 (Streamlit)
# ==========================================

st.set_page_config(page_title="L-BASI Skin OS", page_icon="🧬")

# 타이틀
st.title("🧬 L-BASI™ Skin OS")
st.markdown("### 피부 상태 기반 화장품 루틴 설계 시스템")
st.info("💡 L-BASI는 제품을 추천하는 것이 아니라, 당신의 피부가 **'지금 받아들일 수 있는지'** 판단합니다.")

st.divider()

# --- [STEP 1] 정밀 진단 설문 ---
st.subheader("STEP 1. 정밀 피부 진단 (설문)")
st.caption("현재 피부 상태를 솔직하게 체크해주세요.")

with st.expander("📋 진단 설문지 열기 (클릭)", expanded=True):
    q1 = st.radio("Q1. 화장품을 바를 때 느낌은?", 
                  ["편안하다 (0점)", "가끔 따끔하다 (1점)", "1분 이상 화끈거린다 (3점)", "바르자마자 아프다 (5점)"], index=0)
    
    q2 = st.radio("Q2. 붉은기 상태는?", 
                  ["없다 (0점)", "금방 가라앉는다 (1점)", "항상 붉고 열감 (3점)", "전체적으로 심함 (5점)"], index=0)
    
    q3 = st.radio("Q3. 세안 후 당김은?", 
                  ["없음/약함 (0점)", "부분적 속당김 (1점)", "찢어질 듯 심함 (2점)"], index=0)
    
    q4 = st.radio("Q4. 각질/피부결 상태는?", 
                  ["매끄러움 (0점)", "거칠거칠함 (1점)", "하얀 각질이 일어남 (2점)"], index=0)
    
    q5 = st.radio("Q5. 현재 트러블(여드름)은?", 
                  ["없다 (0점)", "1~2개 (1점)", "5개 이상/화농성 (3점)"], index=0)
    
    q6 = st.radio("Q6. 가려움증이 있나요?", 
                  ["없다 (0점)", "가끔 간질 (1점)", "계속 긁고 싶음 (3점)"], index=0)
    
    st.markdown("---")
    q7 = st.radio("Q7. 최근 3일 내 피부과 시술(레이저, 필링 등)을 받았나요?", ["아니오", "네"], index=0)

# 점수 합산 로직
total_score = sum([extract_score(q) for q in [q1, q2, q3, q4, q5, q6]])
is_procedure = q7

# --- [STEP 2] 화장품 입력 ---
st.divider()
st.subheader("STEP 2. 화장품 목록 입력")
st.caption("사용 중인 기초 화장품 이름을 한 줄에 하나씩 적어주세요.")
products_input = st.text_area("제품명 입력 예시:\n이니스프리 레티놀 앰플\n에스트라 아토베리어 크림", height=150)

# --- [STEP 3] 분석 버튼 및 결과 ---
if st.button("내 루틴 진단하기 🔍", type="primary"):
    if not products_input:
        st.error("화장품 목록을 먼저 입력해주세요.")
    else:
        # 1. 상태 판정 실행
        status = calculate_status(total_score, is_procedure)
        advice = get_advice_text(status)
        
        # 2. 제품 분류 실행
        routine = classify_products(products_input)

        # 3. 결과 화면 출력
        st.divider()
        st.header("📊 L-BASI 분석 결과")
        st.caption(f"진단 점수: {total_score}점 / 판정: {status}")

        # 진단 메시지 박스
        if status == "Normal":
            st.success(advice)
        elif status == "Caution":
            st.info(advice)
        elif status == "Warning":
            st.warning(advice)
        elif status == "Danger":
            st.error(advice)

        # 루틴 재설계 시각화
        st.subheader("🧴 당신의 화장품 재배치 (Routine Map)")
        
        col1, col2, col3 = st.columns(3)

        # Trigger 중단 여부 결정 (Warning 단계 이상이면 중단)
        stop_trigger = (status == "Warning" or status == "Danger")

        with col1:
            st.markdown("### 1. Primer\n*(환경 조성)*")
            if routine["Primer"]:
                for p in routine["Primer"]:
                    st.success(f"Op: {p}")
            else:
                st.caption("제품 없음")

        with col2:
            st.markdown("### 2. Trigger\n*(기능 활성)*")
            if routine["Trigger"]:
                for p in routine["Trigger"]:
                    if stop_trigger:
                        # 위험 단계면 빨간색 취소선
                        st.error(f"⛔ ~~{p}~~ (중단)")
                    elif status == "Caution":
                        # 주의 단계면 노란색 경고
                        st.warning(f"⚠️ {p} (양 줄이기)")
                    else:
                        # 정상 단계면 번개 아이콘
                        st.warning(f"⚡ {p}")
            else:
                st.caption("제품 없음")

        with col3:
            st.markdown("### 3. Stabilizer\n*(안정/유지)*")
            if routine["Stabilizer"]:
                for p in routine["Stabilizer"]:
                    st.info(f"🛡️ {p}")
            else:
                st.caption("제품 없음")

        # 미분류 제품 표시
        if routine["Unknown"]:
            st.caption(f"※ 분류되지 않은 제품: {', '.join(routine['Unknown'])}")
            
        st.divider()
        st.caption("Disclaimer: 본 결과는 AI 알고리즘 기반의 가이드이며 의학적 진단을 대체할 수 없습니다.")
