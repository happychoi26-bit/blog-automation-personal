import os
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 0. 페이지 설정 및 초기화
# -------------------------------------------------------------
st.set_page_config(
    page_title="구글 애드센스 수익화 블로그 공장 (V2.9)",
    page_icon="💰",
    layout="wide"
)

st.title("💰 구글 블로그스팟 수익화 자동화 머신 (V2.9 SEO 분석 분리형)")
st.markdown("Gemini 3.6 Flash + Google Search Grounding / 키워드 최적화 / 429 에러 방지 분리형 구조")

# API 키 설정 (스트리밋 시크릿에서 자동 로드)
with st.sidebar:
    st.header("🔑 API 설정")
    
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

    api_key_input = st.text_input("Google Gemini API Key", type="password", value=default_gemini_key)
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Gemini API Key 자동 연동 완료!")
    else:
        st.warning("Streamlit Secrets에 Gemini API Key를 등록해주세요.")

# 세션 스테이트 초기화
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = ""
if "seo_report" not in st.session_state:
    st.session_state["seo_report"] = ""
if "meta_desc" not in st.session_state:
    st.session_state["meta_desc"] = ""
if "blog_tags" not in st.session_state:
    st.session_state["blog_tags"] = ""
if "last_keyword" not in st.session_state:
    st.session_state["last_keyword"] = ""

# -------------------------------------------------------------
# 1. 3단 탭(Tab) UI 구성
# -------------------------------------------------------------
tab_main, tab_style, tab_seo = st.tabs([
    "📝 키워드 및 본문 생성", 
    "🧠 콘텐츠 스타일 설정", 
    "📊 SEO 분석 및 HTML 리포트"
])

with tab_main:
    st.subheader("1. 공략할 메인 키워드 및 주제 입력")
    target_keyword = st.text_input("메인 키워드 (예: 청년 주택드림 청약통장 조건)", placeholder="구글 상위 노출을 노릴 검색 키워드를 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        content_tone = st.selectbox("글의 어조 (톤앤매너)", ["친근하고 알기 쉬운 블로그체", "전문적이고 객관적인 정보 전달체", "재치 있는 입담체"])
    with col2:
        target_length = st.selectbox("글 분량", ["중간 (모바일 스크롤 최적)", "롱폼 (딥다이브 심층 분석형)"])

    st.markdown("---")
    st.subheader("2. 키워드 4회 최적 분산 전략 선택 (SEO 최적화)")
    keyword_strategy = st.selectbox(
        "타겟 키워드를 본문에 녹여낼 배치 방식을 선택하세요",
        [
            "💡 [추천] 황금 비율 4회 분산 (제목 1회 + 서두 도입부 1회 + 본문 핵심 설명 1회 + 결론 마무리 1회)",
            "🚀 상단 집중형 4회 배치 (제목 1회 + 글 초반부에 연속적으로 3회 집중 배치하여 검색 유입 극대화)",
            "🔀 자연스러운 흐름 분산 (문맥의 자연스러움을 최우선으로 하여 전체 구간에 걸쳐 총 4회 안착)"
        ]
    )

    st.markdown("---")
    st.subheader("3. 추가 강조사항 (Custom Prompt)")
    custom_prompt = st.text_area(
        "본문에 꼭 포함했으면 하는 내용이나 주의사항을 적어주세요",
        placeholder="예: 최신 변경 사항과 혜택을 꼼꼼하게 다뤄 줘.",
        height=100
    )

with tab_style:
    st.subheader("🎨 내 블로그 스타일 레퍼런스")
    my_tone_sample = st.text_area("내가 이전에 썼던 글 중 마음에 드는 문단이나 선호하는 말투를 붙여넣으세요.", height=250, placeholder="예: ~거든요, ~하는 게 좋습니다 등 자주 쓰는 어미 반영")

with tab_seo:
    st.subheader("📊 SEO 분석 및 구글 상위 노출 점검")
    
    # SEO 분석을 따로 실행하는 버튼
    seo_btn = st.button("📊 생성된 본문 SEO 분석 실행하기", type="secondary")
    
    if seo_btn:
        if not api_key_input:
            st.error("사이드바에 Gemini API Key를 입력해주세요!")
        elif not st.session_state["generated_content"]:
            st.warning("💡 먼저 '키워드 및 본문 생성' 탭에서 글을 생성해주세요!")
        else:
            with st.spinner("프로 SEO 에이전트가 모바일 가독성과 키워드 배치를 검수 중입니다..."):
                try:
                    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                    model_name = "gemini-2.5-flash"
                    
                    seo_expert_prompt = f"""
                    너는 15년 경력의 구글 검색 알고리즘(SEO) 및 애드센스 최적화 전문가야.
                    방금 작성된 아래의 블로그 본문과 타겟 키워드를 분석하여, 모바일 가독성과 SEO 관점을 반영한 전문적인 감사(Audit) 리포트를 작성해 줘.

                    [타겟 메인 키워드]: {st.session_state.get('last_keyword', target_keyword)}
                    [분석할 본문]:
                    {st.session_state['generated_content']}

                    [반드시 포함해야 할 채점 항목 및 평가 기준]:
                    1. 키워드 4회 최적 분산 점수 (30점 만점): 메인 키워드가 본문 전체에 걸쳐 정확히 4회 자연스럽게 녹아들었는지 검증.
                    2. 모바일 가독성 및 줄바꿈 점수 (30점 만점): 마크다운 없이 모바일에서 읽기 좋게 1~2줄마다 줄바꿈이 시원하게 잘 적용되었는지 평가.
                    3. 애드센스 승인 적합도 (40점 만점): 최신 팩트체크를 바탕으로 사용자에게 실질적인 가치를 제공하는 글인지 평가.
                    
                    [출력 형식]:
                    - 총점 (100점 만점)
                    - 각 항목별 구체적인 점수 및 냉정한 감점 이유
                    - 구글 상위 노출을 위해 발행 전 반드시 고쳐야 할 실전 개선 팁 2가지
                    """
                    
                    seo_response = client.models.generate_content(model=model_name, contents=seo_expert_prompt)
                    st.session_state["seo_report"] = seo_response.text
                    st.success("SEO 분석이 완료되었습니다!")
                except Exception as e:
                    st.error(f"SEO 분석 중 오류가 발생했습니다: {e}")

    if st.session_state["seo_report"]:
        st.markdown("---")
        st.markdown(st.session_state["seo_report"])

# -------------------------------------------------------------
# 2. 본문 생성 버튼 (실시간 웹 리서치 + 본문)
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("🚀 1단계: 실시간 리서치 + 애드센스 최적화 블로그 글 생성하기", type="primary", use_container_width=True)

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
            
            progress_text.text("🌐 구글 실시간 검색(Search Grounding)으로 최신 트렌드를 팩트체크 후 모바일 최적화 집필 중입니다...")
            
            base_prompt = f"""
            [메인 키워드]: {target_keyword}
            [글의 톤앤매너]: {content_tone}
            [글 분량]: {target_length}
            [키워드 4회 배치 전략]: {keyword_strategy}
            [사용자 추가 요청]: {custom_prompt if custom_prompt else "없음"}
            [말투 참고]: {my_tone_sample if my_tone_sample else "자연스러운 정보성 블로그 후기체"}

            위 조건을 바탕으로 구글 애드센스 승인 및 검색 상위 노출(SEO)에 최적화된 블로그 포스팅을 작성해 줘.
            반드시 구글 실시간 검색 결과를 바탕으로 철저한 팩트체크를 거쳐 정확하고 신뢰도 높은 최신 정보를 포함할 것.
            
            [매우 중요한 모바일 가독성 및 작성 규칙]:
            1. 메인 키워드('{target_keyword}')가 전체 글에서 정확히 총 **4회** 들어가도록 계산해서 배치할 것. (선택된 배치 전략 준수)
            2. '##', '###' 같은 마크다운 소제목 기호나 '**' 같은 강조 기호는 절대로 사용하지 말 것.
            3. **[모바일 가독성 핵심] 스마트폰 화면에서 읽는 독자를 위해, 한 문장이나 두 문장(약 1~2줄)을 쓴 뒤에는 반드시 무조건 엔터(줄바꿈)를 두 번 쳐서 시원시원하고 넓은 여백을 확보할 것. 절대 줄글 형태로 뭉쳐서 쓰지 말 것.**
            4. 100% 긍정적이고 희망찬 마인드셋을 유지할 것 (독자의 불안감을 유발하는 표현 금지).
            5. 글의 맨 마지막 줄에 아래 양식 그대로 '검색 설명'과 '라벨'을 반드시 포함해서 출력할 것:
            
            [METADATA_START]
            검색설명: (구글 검색 결과에 노출될 1~2문장의 핵심 요약문, 메인 키워드 포함)
            라벨: (쉼표로 구분된 태그 2~3개)
            [METADATA_END]
            """
            
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

            st.session_state["last_keyword"] = target_keyword
            st.session_state["seo_report"] = "" # 새 글을 쓰면 기존 SEO 리포트 초기화
            
            progress_text.empty()
            st.success("🎉 모바일 가독성과 팩트체크가 완벽히 적용된 블로그 본문이 생성되었습니다! 'SEO 분석' 탭에서 분석을 진행할 수 있습니다.")
            
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
