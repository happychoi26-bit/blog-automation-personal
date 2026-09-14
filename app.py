import os
import requests
import streamlit as st
from google import genai

# -------------------------------------------------------------
# 0. 페이지 설정 및 초기화
# -------------------------------------------------------------
st.set_page_config(
    page_title="구글 애드센스 수익화 블로그 공장",
    page_icon="💰",
    layout="wide"
)

st.title("💰 구글 블로그스팟 수익화 자동화 머신 (V2)")
st.markdown("Gemini Flash 기반 / 정보성 키워드 타겟 / Unsplash 자동 이미지 매칭 및 SEO 최적화")

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("🔑 API 설정")
    api_key_input = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Gemini API Key 설정 완료!")
    else:
        st.warning("Google AI Studio API Key를 입력해주세요.")
        
    st.markdown("---")
    st.markdown("### 🖼️ Unsplash 이미지 API (선택)")
    unsplash_key = st.text_input("Unsplash Access Key", type="password", help="이미지 자동 검색용 (없어도 텍스트 가이드는 작동합니다)")

# 세션 스테이트 초기화
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = ""
if "seo_report" not in st.session_state:
    st.session_state["seo_report"] = ""
if "matched_images" not in st.session_state:
    st.session_state["matched_images"] = []

# -------------------------------------------------------------
# 1. Unsplash 이미지 자동 검색 함수
# -------------------------------------------------------------
def fetch_unsplash_images(query: str, client_key: str):
    if not client_key:
        return []
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {client_key}"}
    params = {"query": query, "per_page": 3, "lang": "ko"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            results = res.json().get("results", [])
            return [img["urls"]["regular"] for img in results]
    except Exception:
        pass
    return []

# -------------------------------------------------------------
# 2. 3단 탭(Tab) UI 구성 (수익화 맞춤형)
# -------------------------------------------------------------
tab_main, tab_style, tab_seo = st.tabs([
    "📝 키워드 및 본문 생성", 
    "🧠 콘텐츠 스타일 설정", 
    "📊 SEO 분석 및 HTML 리포트"
])

with tab_main:
    st.subheader("1. 공략할 메인 키워드 및 주제 입력")
    target_keyword = st.text_input("메인 키워드 (예: 2026 청년 주택드림 청약통장 조건, 연말정산 환급금 조회 방법)", placeholder="구글 상위 노출을 노릴 검색 키워드를 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        content_tone = st.selectbox("글의 어조 (톤앤매너)", ["친근하고 알기 쉬운 블로그체", "전문적이고 객관적인 정보 전달체", "재치 있는 입담체"])
    with col2:
        target_length = st.selectbox("글 분량", ["중간 (공인 가독성 최적)", "롱폼 (딥다이브 심층 분석형)"])

    st.markdown("---")
    st.subheader("2. 추가 강조사항 (Custom Prompt)")
    custom_prompt = st.text_area(
        "본문에 꼭 포함했으면 하는 내용이나 주의사항을 적어주세요",
        placeholder="예: 신청 기한이 얼마 안 남았다는 점을 강조하고, 핵심 요약을 서두에 배치해 줘.",
        height=100
    )

with tab_style:
    st.subheader("🎨 내 블로그 스타일 레퍼런스")
    my_tone_sample = st.text_area("내가 이전에 썼던 글 중 마음에 드는 문단이나 선호하는 말투를 붙여넣으세요.", height=250, placeholder="예: ~거든요, ~하는 게 좋습니다 등 자주 쓰는 어미 반영")

with tab_seo:
    st.subheader("📊 SEO 분석 및 구글 상위 노출 점검")
    if st.session_state["seo_report"]:
        st.markdown(st.session_state["seo_report"])
    else:
        st.info("💡 아직 분석 리포트가 없습니다. 첫 번째 탭에서 글을 생성해주세요!")

# -------------------------------------------------------------
# 3. AI 파이프라인 가동 버튼
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("🚀 애드센스 최적화 블로그 글 생성하기", type="primary", use_container_width=True)

if generate_btn:
    if not api_key_input:
        st.error("사이드바에 Gemini API Key를 입력해주세요!")
    elif not target_keyword:
        st.error("공략할 메인 키워드를 입력해주세요!")
    else:
        progress_text = st.empty()
        
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            model_name = "gemini-2.5-flash"  # 안정적인 최신 플래시 모델 명칭 적용
            
            # 1. Unsplash 이미지 자동 수급
            progress_text.text("🖼️ [1단계] Unsplash에서 관련 고화질 이미지를 탐색 중...")
            images = fetch_unsplash_images(target_keyword, unsplash_key)
            st.session_state["matched_images"] = images
            
            img_guide = "\n".join([f"- 이미지 URL {i+1}: {url}" for i, url in enumerate(images)]) if images else "Unsplash API 키 미입력 (텍스트 내 이미지 가이드로 대체)"

            # 2. 본문 생성 에이전트
            progress_text.text("✍️ [2단계] 라이터 에이전트가 구글 SEO 맞춤형 정보성 글을 작성 중입니다...")
            
            base_prompt = f"""
            [메인 키워드]: {target_keyword}
            [글의 톤앤매너]: {content_tone}
            [글 분량]: {target_length}
            [사용자 추가 요청]: {custom_prompt if custom_prompt else "없음"}
            [말투 참고]: {my_tone_sample if my_tone_sample else "자연스러운 정보성 블로그 후기체"}
            [확보된 이미지 소스]:
            {img_guide}

            위 조건을 바탕으로, 구글 애드센스 승인 및 검색 상위 노출(SEO)에 최적화된 블로그 본문을 작성해 줘.
            - H2, H3 소제목을 적극 활용할 것.
            - 가독성이 좋게 핵심 내용은 불릿 포인트나 표 형태로 정리할 것.
            - 본문 중간중간 적절한 위치에 확보된 이미지 소스의 URL을 마크다운 이미지 형식(![](URL))으로 삽입할 것.
            """
            
            body_response = client.models.generate_content(model=model_name, contents=base_prompt)
            st.session_state["generated_content"] = body_response.text

            # 3. SEO 리포트 생성 에이전트
            progress_text.text("📊 [3단계] SEO 분석 에이전트가 구글 알고리즘 기준 적합도를 채점 중입니다...")
            seo_prompt = f"다음은 방금 작성된 블로그 본문입니다:\n\n{body_response.text}\n\n이 글을 바탕으로 구글 SEO(키워드 밀도, 가독성, 구조화 데이터) 관점에서 100점 만점 점수와 개선 피드백을 마크다운 리포트로 작성해 줘."
            seo_response = client.models.generate_content(model=model_name, contents=seo_prompt)
            st.session_state["seo_report"] = seo_response.text
            
            progress_text.empty()
            st.success("🎉 수익화용 블로그 글 및 SEO 리포트 생성이 완료되었습니다!")
            
        except Exception as e:
            progress_text.empty()
            st.error(f"오류가 발생했습니다: {e}")

# 결과 출력 영역
if st.session_state["generated_content"]:
    st.markdown("---")
    st.subheader("📄 최종 생성된 블로그 초안 (복사해서 블로그스팟에 붙여넣으세요)")
    st.text_area("블로그 본문 출력", value=st.session_state["generated_content"], height=500)
    
    if st.session_state["matched_images"]:
        st.subheader("🖼️ 본문에 자동 매칭된 고화질 이미지 미리보기")
        cols = st.columns(len(st.session_state["matched_images"]))
        for i, img_url in enumerate(st.session_state["matched_images"]):
            with cols[i]:
                st.image(img_url, caption=f"이미지 {i+1}", use_column_width=True)
