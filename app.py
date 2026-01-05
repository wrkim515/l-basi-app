import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# ==========================================
# 1. 핵심 로직 (AI 두뇌)
# ==========================================

# OCR 리더기 (한 번만 로딩)
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['ko', 'en'], gpu=False)

def extract_text_from_image(image_file):
    """이미지에서 글자를 읽어오는 함수"""
    reader = load_ocr_reader()
    image = Image.open(image_file)
    image_np = np.array(image)
    result = reader.readtext(image_np, detail=0)
    return "\n".join(result)

def classify_products(products_text):
    """입력된 모든 텍스트를 분석하여 분류"""
    # 키워드 DB
    triggers_keywords = ["레티놀", "비타민C", "아하", "바하", "AHA", "BHA", "필링", "스크럽", "미백", "주름", "고기능", "애시드", "L-AA", "엔자임", "박피", "살리실릭", "글라이콜릭"]
    primers_keywords = ["토너", "스킨", "로션", "세라마이드", "장벽", "보습", "수분", "히알루론산", "크림", "에센스", "부스터", "프라이머", "글리세린", "베타인", "판테놀"]
    stabilizers_keywords = ["시카", "진정", "재생", "마데카", "리페어", "오일", "밤", "병풀", "알로에", "쑥", "어성초", "알란토인", "캄"]

    my_routine = {"Primer": [], "Trigger": [], "Stabilizer": [], "Unknown": []}
    
    # 텍스트 정리 (쉼표나 줄바꿈으로 구분된 것들을 리스트로 만듦)
    clean_text = products_text.replace(",", "\n")
    product_list = [p.strip() for p in clean_text.split('\n') if p.strip()]

    for product in product_list:
        classified = False
        # 1순위 Trigger
        for key in triggers_keywords:
            if key in product:
                my_routine["Trigger"].append(product)
                classified = True
                break
        # 2순위 Stabilizer
        if not classified:
            for key in stabilizers_keywords:
                if key in product:
                    my_routine["Stabilizer"].append(product)
                    classified = True
                    break
        # 3순위 Primer
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
st.markdown("### 피부 상태 기반 화장품 루틴 설계 시스템")
st.info("💡 **제품명**을 적거나 **성분표 사진**을 올려주세요. 정보가 많을수록 정확해집니다!")

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

# --- [STEP 2] 화장품 입력 (통합형) ---
st.divider()
st.subheader("STEP 2. 화장품 등록")
st.caption("제품명이나 전성분표, 둘 중 하나만 있어도 됩니다. (둘 다 하면 더 좋아요!)")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.markdown("**✍️ 1. 제품명/성분 직접 입력**")
    manual_text = st.text_area("텍스트 입력", height=150, placeholder="예: 레티놀 앰플, 정제수, 글리세린...")

with col_input2:
    st.markdown("**📷 2. 전성분표 사진 업로드**")
    uploaded_file = st.file_uploader("사진 올리기", type=['png', 'jpg', 'jpeg'])
    ocr_text = ""
    if uploaded_file is not None:
        with st.spinner("AI가 글자를 읽는 중..."):
            try:
                ocr_text = extract_text_from_image(uploaded_file)
                st.success("사진 읽기 성공!")
                with st.expander("읽은 내용 확인"):
                    st.text(ocr_text)
            except:
                st.error("사진을 읽을 수 없습니다.")

# 두 입력값 합치기
final_input = manual_text + "\n" + ocr_text

# --- [STEP 3] 결과 출력 ---
if st.button("내 루틴 진단하기 🔍", type="primary"):
    if not final_input.strip():
        st.error("제품명을 적거나 사진을 올려주세요! (최소 한 가지 필요)")
    else:
        status = calculate_status(total_score, q7)
        advice = get_advice_text(status)
        routine = classify_products(final_input)

        st.divider()
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
            if routine["Primer"]:
                for p in routine["Primer"]: st.success(p)
            else: st.caption("없음")
        
        with c2:
            st.markdown("### 2. Trigger")
            if routine["Trigger"]:
                for p in routine["Trigger"]:
                    if stop_trigger: st.error(f"⛔ ~~{p}~~")
                    elif status == "Caution": st.warning(f"⚠️ {p}")
                    else: st.warning(f"⚡ {p}")
            else: st.caption("없음")
            
        with c3:
            st.markdown("### 3. Stabilizer")
            if routine["Stabilizer"]:
                for p in routine["Stabilizer"]: st.info(p)
            else: st.caption("없음")

        # 미분류 정보
        if routine["Unknown"]:
            with st.expander("분류되지 않은 텍스트 보기"):
                st.caption(", ".join(routine['Unknown']))
