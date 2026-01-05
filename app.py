import streamlit as st
import re

# ==========================================
# 1. 핵심 로직 (L-BASI 엔진)
# ==========================================

def classify_products(text_data):
    """
    제품명과 전성분 텍스트를 통합 분석하여 분류
    """
    # 키워드 데이터베이스 (지속적 업데이트 필요)
    triggers_keywords = ["레티놀", "비타민C", "아스코빅", "아하", "바하", "AHA", "BHA", "살리실릭", "글라이콜릭", "락틱", "필링", "스크럽", "미백", "주름", "고기능", "애시드", "L-AA", "엔자임", "박피", "나이아신아마이드"]
    primers_keywords = ["토너", "스킨", "로션", "세라마이드", "장벽", "보습", "수분", "히알루론산", "소듐하이알루로네이트", "크림", "에센스", "부스터", "프라이머", "글리세린", "베타인", "판테놀", "콜레스테롤", "지방산"]
    stabilizers_keywords = ["시카", "진정", "재생", "마데카", "리페어", "오일", "밤", "병풀", "알로에", "쑥", "어성초", "알란토인", "캄", "카모마일", "녹차"]

    my_routine = {"Primer": [], "Trigger": [], "Stabilizer": [], "Unknown": []}
    
    # 텍스트가 비어있지 않은 경우에만 분석
    if text_data:
        classified = False
        # 1순위: Trigger (자극 성분 우선 감지)
        for key in triggers_keywords:
            if key in text_data:
                my_routine["Trigger"].append(text_data) # 전체 텍스트를 해당 카테고리에 넣음
                classified = True
                break
        
        # 2순위: Stabilizer
        if not classified:
            for key in stabilizers_keywords:
                if key in text_data:
                    my_routine["Stabilizer"].append(text_data)
                    classified = True
                    break
        
        # 3순위: Primer
        if not classified:
            for key in primers_keywords:
                if key in text_data:
                    my_routine["Primer"].append(text_data)
                    classified = True
                    break
        
        # 미분류
        if not classified:
            my_routine["Unknown"].append(text_data)
            
    return my_routine

def calculate_status(score, is_procedure):
    if is_procedure == "네":
        if score >= 10: return "Danger"
        return "Warning" 
    
    if score >= 10: return "Danger"
    elif score >= 6: return "Warning"
    elif score >= 3: return "Caution"
    else: return "Normal"

def get_advice_text(status):
    if status == "Normal":
        return """
        ✅ **안정(Stable) 단계입니다.**
        피부 컨디션이 최적입니다! **Trigger(기능성) 제품**을 적극적으로 사용하여 효과를 보세요.
        """
    elif status == "Caution":
        return """
        🙂 **주의(Caution)가 필요합니다.**
        장벽이 살짝 약해져 있습니다. **Trigger 제품 양을 절반**으로 줄이고, 수분 공급(Primer)에 집중하세요.
        """
    elif status == "Warning":
        return """
        ✋ **경고(Warning) 단계입니다. Trigger를 멈추세요.**
        피부가 자극 신호를 보내고 있습니다. **모든 Trigger(기능성) 사용을 중단**하고, 장벽 복구(Primer)만 하세요.
        """
    elif status == "Danger":
        return """
        🚨 **위험(Danger) 단계입니다.**
        피부 방어선이 무너졌습니다. 모든 화장품을 끊고, **순한 세안제와 진정 크림(Stabilizer)**만 사용하세요.
        """
    return ""

def extract_score(text):
    match = re.search(r'\((\d+)점\)', text)
    return int(match.group(1)) if match else 0


# ==========================================
# 2. 웹사이트 화면 구성
# ==========================================

st.set_page_config(page_title="L-BASI Skin OS", page_icon="🧬")

st.title("🧬 L-BASI™ Skin OS")
st.markdown("### 정밀 성분 분석 기반 루틴 가이드")
st.info("💡 **전성분**을 직접 넣어주시면, 병원급 정밀도로 분석해 드립니다.")

st.divider()

# --- [STEP 1] 진단 설문 ---
st.subheader("STEP 1. 정밀 피부 진단")
with st.expander("📋 진단 설문지 열기 (클릭)", expanded=True):
    q1 = st.radio("Q1. 화장품 바를 때 느낌?", ["편안하다 (0점)", "가끔 따끔 (1점)", "화끈거림 (3점)", "아프다 (5점)"])
    q2 = st.radio("Q2. 붉은기 상태?", ["없다 (0점)", "금방 가라앉음 (1점)", "항상 붉음 (3점)", "심함 (5점)"])
    q3 = st.radio("Q3. 세안 후 당김?", ["없음 (0점)", "속당김 (1점)", "심함 (2점)"])
    q4 = st.radio("Q4. 각질 상태?", ["매끄러움 (0점)", "거칠함 (1점)", "하얀 각질 (2점)"])
    q5 = st.radio("Q5. 트러블?", ["없다 (0점)", "1~2개 (1점)", "5개 이상 (3점)"])
    q6 = st.radio("Q6. 가려움?", ["없다 (0점)", "가끔 (1점)", "계속 (3점)"])
    st.markdown("---")
    q7 = st.radio("Q7. 최근 3일 내 시술 여부?", ["아니오", "네"])

total_score = sum([extract_score(q) for q in [q1, q2, q3, q4, q5, q6]])

# --- [STEP 2] 화장품 입력 (세트 입력 방식) ---
st.divider()
st.subheader("STEP 2. 화장품 등록 (정밀 분석)")
st.caption("사용 중인 제품을 하나씩 등록해주세요.")

# 세션 스테이트를 사용해 입력된 제품 목록 저장
if 'product_list' not in st.session_state:
    st.session_state.product_list = []

with st.form("product_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        p_name = st.text_input("제품명 (별명)", placeholder="예: 이니스프리 레티놀")
    with col2:
        p_ingredients = st.text_area("전성분 붙여넣기", placeholder="인터넷에서 전성분을 복사해서 여기에 붙여넣으세요.", height=100)
    
    submitted = st.form_submit_button("제품 추가하기 ➕")
    
    if submitted and p_name:
        # 제품명과 전성분을 합쳐서 저장
        combined_text = f"{p_name} | {p_ingredients}"
        st.session_state.product_list.append(combined_text)
        st.success(f"'{p_name}' 추가됨!")

# 등록된 제품 목록 보여주기
if st.session_state.product_list:
    st.markdown("##### 🛒 분석 대기 중인 제품 목록")
    for idx, p in enumerate(st.session_state.product_list):
        st.text(f"{idx+1}. {p.split('|')[0]}") # 제품명만 보여줌
        
    if st.button("목록 초기화 🗑️"):
        st.session_state.product_list = []
        st.rerun()

# --- [STEP 3] 결과 출력 ---
st.divider()
if st.button("내 루틴 진단하기 🔍", type="primary"):
    if not st.session_state.product_list:
        st.error("위에서 제품을 최소 1개 이상 추가해주세요!")
    else:
        status = calculate_status(total_score, q7)
        advice = get_advice_text(status)
        
        # 저장된 모든 제품 분석
        final_routine = {"Primer": [], "Trigger": [], "Stabilizer": [], "Unknown": []}
        
        for item_text in st.session_state.product_list:
            # 개별 제품 분석 결과 가져오기
            result = classify_products(item_text)
            # 결과 합치기
            for key in result:
                final_routine[key].extend(result[key])

        st.header("📊 L-BASI 분석 결과")
        
        # 상태 메시지
        if status == "Normal": st.success(advice)
        elif status == "Caution": st.info(advice)
        elif status == "Warning": st.warning(advice)
        elif status == "Danger": st.error(advice)

        # 루틴 결과
        st.subheader("🧴 성분 기반 재분류")
        c1, c2, c3 = st.columns(3)
        stop_trigger = (status == "Warning" or status == "Danger")

        with c1:
            st.markdown("### 1. Primer")
            for p in final_routine["Primer"]:
                name = p.split('|')[0]
                st.success(name)
        
        with c2:
            st.markdown("### 2. Trigger")
            for p in final_routine["Trigger"]:
                name = p.split('|')[0]
                if stop_trigger: st.error(f"⛔ ~~{name}~~")
                elif status == "Caution": st.warning(f"⚠️ {name}")
                else: st.warning(f"⚡ {name}")
            
        with c3:
            st.markdown("### 3. Stabilizer")
            for p in final_routine["Stabilizer"]:
                name = p.split('|')[0]
                st.info(name)

        if final_routine["Unknown"]:
            with st.expander("분류되지 않은 제품 보기"):
                for p in final_routine["Unknown"]:
                    st.caption(p.split('|')[0])
