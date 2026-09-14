import os
import requests
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 0. 페이지 설정 및 초기화
# -------------------------------------------------------------
st.set_page_config(
    page_title="구글 애드센스 수익화 블로그 공장 (V2.5 실시간 리서치)",
    page_icon="💰",
    layout="wide"
)

st.title("💰 구글 블로그스팟 수익화 자동화 머신 (V2.5 실시간 트렌드 리서치)")
st.markdown("Gemini Flash + Google Search Grounding / 실시간 웹 리서치 / Unsplash 자동 이미지 / 프로 SEO")

# API 키 설정 (스트리밋 시크릿에서 자동 로드)
with st.sidebar:
    st.header("🔑 API 설정")
    
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    default_unsplash_key = st.secrets.get("UNSPLASH_ACCESS_KEY", "")

    api_key_input = st.text_input("Google Gemini API Key", type="password", value=default_gemini_key)
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Gemini API Key 자동 연동 완료!")
    else:
        st.warning("Streamlit Secrets에 Gemini API Key를 등록해주세요.")
        
    st.markdown("---")
    st.markdown("### 🖼️ Unsplash 이미지 API")
    unsplash_key = st.text_input("Unsplash Access Key", type="password", value=default_unsplash_key)

# 세션 스테이트 초기화
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = ""
if "seo_report" not in st.session_state:
    st.session_state["seo_report"] = ""
if "meta_desc" not in st.session_state:
    st.session_state["meta_desc"] = ""
if "blog_tags" not in st.session_state:
    st.session_state["blog_tags"] = ""
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
# 2. 3단 탭(Tab) UI 구성
# -------------------------------------------------------------
tab_main, tab_style, tab_seo = st.tabs([
    "📝 키워드 및 본문 생성", 
    "🧠 콘텐츠 스타일 설정", 
    "📊 SEO 분석 및 HTML 리포트"
])

with tab_main:
    st.subheader("1. 공략할 메인 키워드 및 주제 입력")
    target_keyword = st.text_input("메인 키워드 (예: 2026 청년 주택드림 청약통장 조건)", placeholder="구글 상위 노출을 노릴 검색 키워드를 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        content_tone = st.selectbox("글의 어조 (톤앤매너)", ["친근하고 알기 쉬운 블로그체", "전문적이고 객관적인 정보 전달체", "재치 있는 입담체"])
    with col2:
        target_length = st.selectbox("글 분량", ["중간 (공인 가독성 최적)", "롱폼 (딥다이브 심층 분석형)"])

    st.markdown("---")
    st.subheader("2. 추가 강조사항 (Custom Prompt)")
    custom_prompt = st.text_area(
        "본문에 꼭 포함했으면 하는 내용이나 주의사항을 적어주세요",
        placeholder="예: 신청 기한이 얼마 안 남았다는 점을 강조하고, 최신 2026년 기준 변경 사항을 반영해 줘.",
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
        st.info("💡 아직 분석 리포트가 없습니다. '키워드 및 본문 생성' 탭에서 글을 먼저 생성해주세요!")

# -------------------------------------------------------------
# 3. AI 파이프라인 가동 버튼 (실시간 웹 리서치 + 본문 + SEO)
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("🚀 실시간 리서치 + 애드센스 최적화 블로그 글 생성하기", type="primary", use_container_width=True)

if generate_btn:
    if not api_key_input:
        st.error("사이드바에 Gemini API Key를 입력해주세요!")
    elif not target_keyword:
        st.error("공략할 메인 키워드를 입력해주세요!")
    else:
        progress_text = st.empty()
        
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            model_name = "gemini-2.5-flash"
            
            # 1. Unsplash 이미지 자동 수급
            progress_text.text("🖼️ [1단계] Unsplash에서 관련 고화질 이미지를 탐색 중입니다...")
            images = fetch_unsplash_images(target_keyword, unsplash_key)
            st.session_state["matched_images"] = images
            
            img_guide = "\n".join([f"- 이미지 URL {i+1}: {url}" for i, url in enumerate(images)]) if images else "Unsplash API 키 미입력 (텍스트 내 이미지 가이드로 대체)"

            # 2. 실시간 웹 리서치 및 본문 생성 (Google Search Grounding 활성화)
            progress_text.text("🌐 [2단계] 구글 실시간 검색(Search Grounding)을 통해 최신 트렌드와 정보를 리서치 후 집필 중입니다...")
            
            base_prompt = f"""
            [메인 키워드]: {target_keyword}
            [글의 톤앤매너]: {content_tone}
            [글 분량]: {target_length}
            [사용자 추가 요청]: {custom_prompt if custom_prompt else "없음"}
            [말투 참고]: {my_tone_sample if my_tone_sample else "자연스러운 정보성 블로그 후기체"}
            [확보된 이미지 소스]:
            {img_guide}

            위 조건을 바탕으로 구글 애드센스 승인 및 검색 상위 노출(SEO)에 최적화된 블로그 포스팅을 작성해 줘.
            반드시 최신 웹 검색 결과를 반영하여 정확하고 신뢰도 높은 최신 정보(2026년 기준)를 포함해 작성할 것.
            
            [중요 작성 규칙]:
            1. '##', '###' 같은 마크다운 소제목 기호나 '**' 같은 강조 기호는 절대로 사용하지 말 것.
            2. 대신 자연스러운 줄바꿈, 빈 줄, 그리고 이모지(💡, ✅ 등)를 활용해 사람이 쓴 것처럼 가독성 있게 작성할 것.
            3. 핵심 내용은 깔끔한 기호(예: -, ㆍ)나 번호 매기기로 정리할 것.
            4. 글의 맨 마지막 줄에 아래 양식 그대로 '검색 설명'과 '라벨'을 반드시 포함해서 출력할 것:
            
            [METADATA_START]
            검색설명: (구글 검색 결과에 노출될 1~2문장의 핵심 요약문, 메인 키워드 포함)
            라벨: (쉼표로 구분된 태그 2~3개)
            [METADATA_END]
            """
            
            # 구글 실시간 검색 툴(Google Search) 장착 옵션 설정
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
            
            body_response = client.models.generate_content(
                model=model_name, 
                contents=base_prompt,
                config=config
            )
            full_text = body_response.text

            # 본문과 메타데이터 분리 파싱
            if "[METADATA_START]" in full_text and "[METADATA_END]" in full_text:
                parts = full_text.split("[METADATA_START]")
                st.session_state["generated_content"] = parts[0].strip()
                
                meta_part = parts[1].split("[METADATA_END]")[0].strip()
                for line in meta_part.split("\n"):
                    if "검색설명:" in line:
                        st.session_state["meta_desc"] = line.replace("검색설명:", "").strip()
                    elif "라벨:" in line:
                        st.session_state["blog_tags"] = line.replace("라벨:", "").strip()
            else:
                st.session_state["generated_content"] = full_text
                st.session_state["meta_desc"] = "정보성 블로그 포스팅입니다."
                st.session_state["blog_tags"] = target_keyword

            # 3. 프로 SEO 분석 에이전트
            progress_text.text("📊 [3단계] 프로 SEO 에이전트가 구글 알고리즘 기준으로 깐깐하게 채점 중입니다...")
            
            seo_expert_prompt = f"""
            너는 15년 경력의 구글 검색 알고리즘(SEO) 및 애드센스 최적화 전문가야.
            방금 작성된 아래의 블로그 본문과 타겟 키워드를 분석하여, 허위 없는 실제 전문가 수준의 SEO 감사(Audit) 리포트를 작성해 줘.

            [타겟 메인 키워드]: {target_keyword}
            [분석할 본문]:
            {st.session_state['generated_content']}

            [반드시 포함해야 할 채점 항목 및 평가 기준]:
            1. 키워드 최적화 점수 (30점 만점): 서두 100자 이내에 메인 키워드가 포함되었는지, 본문 내 키워드 밀도가 적정한지 평가.
            2. 구조 및 가독성 점수 (30점 만점): AI 티 나는 마크다운 기호 없이 단락이 깔끔하게 나뉘었는지, 리스트나 기호 정리가 잘 되었는지 평가.
            3. 애드센스 승인 적합도 (40점 만점): 사용자에게 실질적인 정보(조건, 방법, 최신성 등)를 제공하는 퀄리티 높은 글인지 평가.
            
            [출력 형식]:
            - 총점 (100점 만점)
            - 각 항목별 구체적인 점수 및 냉정한 감점 이유
            - 구글 상위 노출을 위해 발행 전 반드시 고쳐야 할 실전 개선 팁 2가지
            """
            
            seo_response = client.models.generate_content(model=model_name, contents=seo_expert_prompt)
            st.session_state["seo_report"] = seo_response.text
            
            progress_text.empty()
            st.success("🎉 실시간 웹 리서치와 SEO 분석이 완료된 고품질 블로그 패키지가 생성되었습니다!")
            
        except Exception as e:
            progress_text.empty()
            st.error(f"오류가 발생했습니다: {e}")

# 결과 출력 영역
if st.session_state["generated_content"]:
    st.markdown("---")
    st.subheader("📄 블로그스팟 세팅용 원클릭 패키지")
    
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.text_input("📌 복사해서 넣을 [검색 설명]", value=st.session_state.get("meta_desc", ""))
    with col_meta2:
        st.text_input("🏷️ 복사해서 넣을 [라벨 (태그)]", value=st.session_state.get("blog_tags", ""))

    st.text_area("📄 블로그 본문 출력 (복사해서 블로그스팟에 붙여넣으세요)", value=st.session_state["generated_content"], height=400)
    
    if st.session_state["matched_images"]:
        st.subheader("🖼️ 본문에 자동 매칭된 고화질 이미지 미리보기")
        cols = st.columns(len(st.session_state["matched_images"]))
        for i, img_url in enumerate(st.session_state["matched_images"]):
            with cols[i]:
                st.image(img_url, caption=f"이미지 {i+1}", use_container_width=True)
