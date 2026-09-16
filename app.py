import os
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 0. 페이지 설정 및 초기화
# -------------------------------------------------------------
st.set_page_config(
    page_title="통합 블로그 자동화 공장 (V2.20 멀티 플랫폼 최적화)",
    page_icon="💰",
    layout="wide"
)

st.title("💰 네이버 & 구글 블로그 통합 수익화 자동화 머신 (V2.20)")
st.markdown("Gemini 3.6 Flash / 2500자 딥다이브 롱폼 · 해시태그 · 모바일 가독성 최적화")

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
if "naver_hashtags" not in st.session_state:
    st.session_state["naver_hashtags"] = ""
if "naver_category" not in st.session_state:
    st.session_state["naver_category"] = ""
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
    target_keyword = st.text_input("메인 키워드 (예: 청년 주택드림 청약통장 조건)", placeholder="상위 노출을 노릴 검색 키워드를 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        content_tone = st.selectbox("글의 어조 (톤앤매너)", ["친근하고 알기 쉬운 블로그체", "전문적이고 객관적인 정보 전달체", "재치 있는 입담체"])
    with col2:
        target_platform = st.selectbox("주요 타겟 플랫폼", ["네이버 블로그 최적화 (해시태그/가독성 강화)", "구글 블로그스팟 최적화 (HTML/SEO 메타포맷)"])

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
        placeholder="예: 최신 변경 사항과 혜택, 실질적인 팁을 꼼꼼하게 다뤄 줘.",
        height=100
    )

with tab_style:
    st.subheader("🎨 내 블로그 스타일 레퍼런스")
    my_tone_sample = st.text_area("내가 이전에 썼던 글 중 마음에 드는 문단이나 선호하는 말투를 붙여넣으세요.", height=250, placeholder="예: ~거든요, ~하는 게 좋습니다 등 자주 쓰는 어미 반영")

with tab_seo:
    st.subheader("📊 SEO 분석 및 상위 노출 점검")
    
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
                    model_name = "gemini-3.6-flash"
                    
                    seo_expert_prompt = f"""
                    너는 15년 경력의 네이버/구글 검색 알고리즘 및 콘텐츠 마케팅 전문가야.
                    방금 작성된 아래의 블로그 본문과 타겟 키워드를 분석하여, 모바일 가독성과 SEO 관점을 반영한 전문적인 감사(Audit) 리포트를 작성해 줘.

                    [타겟 메인 키워드]: {st.session_state.get('last_keyword', target_keyword)}
                    [분석할 본문]:
                    {st.session_state['generated_content']}

                    [반드시 포함해야 할 채점 항목 및 평가 기준]:
                    1. 키워드 4회 최적 분산 점수 (30점 만점): 메인 키워드가 본문 전체에 걸쳐 정확히 4회 자연스럽게 녹아들었는지 검증.
                    2. 모바일 가독성 및 여백 점수 (30점 만점): 모바일에서 읽기 좋게 충분한 줄바꿈과 여백이 확보되었는지 평가.
                    3. 콘텐츠 깊이 및 분량 점수 (40점 만점): 2500자 이상의 풍부한 정보와 실질적 가치를 제공하는지 평가.
                    
                    [출력 형식]:
                    - 총점 (100점 만점)
                    - 각 항목별 구체적인 점수 및 냉정한 감점 이유
                    - 상위 노출을 위해 발행 전 반드시 고쳐야 할 실전 개선 팁 2가지
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
# 2. 본문 생성 버튼 (2500자 롱폼 & 가독성 강화)
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("🚀 1단계: 2500자 딥다이브 블로그 글 생성하기", type="primary", use_container_width=True)

if generate_btn:
    if not api_key_input:
        st.error("사이드바에 Gemini API Key를 입력해주세요!")
    elif not target_keyword:
        st.error("공략할 메인 키워드를 입력해주세요!")
    else:
        progress_text = st.empty()
        
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            model_name = "gemini-3.6-flash"
            
            progress_text.text("✍️ Gemini 3.6 모델이 2500자 이상의 심층 블로그 포스팅을 집필 중입니다...")
            
            base_prompt = f"""
            [메인 키워드]: {target_keyword}
            [글의 톤앤매너]: {content_tone}
            [주요 타겟 플랫폼]: {target_platform}
            [키워드 4회 배치 전략]: {keyword_strategy}
            [사용자 추가 요청]: {custom_prompt if custom_prompt else "없음"}
            [말투 참고]: {my_tone_sample if my_tone_sample else "자연스러운 정보성 블로그 후기체"}

            위 조건을 바탕으로 네이버 및 구글 검색 상위 노출(SEO)에 최적화된 심층 블로그 포스팅을 작성해 줘.
            
            [필수 작성 규칙 및 분량 제약]:
            1. **[분량 확보] 공백 포함 총 2,500자 이상의 충분하고 깊이 있는 롱폼(Long-form) 분량으로 작성할 것. (대충 쓰지 말고 세부 항목, 장단점, 이용 팁, Q&A 등을 상세히 서술하여 길이를 채울 것)**
            2. 메인 키워드('{target_keyword}')가 전체 글에서 정확히 총 **4회** 들어가도록 계산해서 배치할 것. (선택된 배치 전략 준수)
            3. '##', '###' 같은 무거운 마크다운 소제목 기호나 '**' 같은 강조 기호는 절대로 사용하지 말 것.
            4. **[모바일 가독성 및 여백 핵심] 스마트폰 화면에서 읽는 독자를 위해, 한 문장이나 두 문장(약 1~2줄)을 쓴 뒤에는 반드시 엔터(줄바꿈)를 두 번 쳐서 시원시원하고 넓은 여백과 들여쓰기 느낌의 가독성을 확보할 것. 절대 줄글 형태로 뭉쳐서 쓰지 말 것.**
            5. 100% 긍정적이고 희망찬 마인드셋을 유지할 것 (독자의 불안감을 유발하는 표현 금지).
            6. 글의 맨 마지막 줄에 아래 양식 그대로 메타데이터 및 네이버 최적화 요소를 반드시 포함해서 출력할 것:
            
            [METADATA_START]
            검색설명: (검색 결과에 노출될 1~2문장의 핵심 요약문, 메인 키워드 포함)
            라벨: (블로그스팟용 태그 2~3개)
            네이버카테고리: (네이버 블로그에 어울리는 추천 발행 카테고리 이름 1개)
            네이버해시태그: (#키워드1 #키워드2 #키워드3 #키워드4 등 5~7개 공백 구분 해시태그)
            [METADATA_END]
            """
            
            body_response = client.models.generate_content(
                model=model_name, 
                contents=base_prompt
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
                    elif "네이버카테고리:" in line:
                        st.session_state["naver_category"] = line.replace("네이버카테고리:", "").strip()
                    elif "네이버해시태그:" in line:
                        st.session_state["naver_hashtags"] = line.replace("네이버해시태그:", "").strip()
            else:
                st.session_state["generated_content"] = full_text
                st.session_state["meta_desc"] = "정보성 블로그 포스팅입니다."
                st.session_state["blog_tags"] = target_keyword
                st.session_state["naver_category"] = "일상·생각"
                st.session_state["naver_hashtags"] = f"#{target_keyword.replace(' ', '')}"

            st.session_state["last_keyword"] = target_keyword
            st.session_state["seo_report"] = "" 
            
            progress_text.empty()
            st.success("🎉 2500자 이상의 심층 블로그 본문이 생성되었습니다!")
            
        except Exception as e:
            progress_text.empty()
            st.error(f"오류가 발생했습니다: {e}")

# 결과 출력 영역
if st.session_state["generated_content"]:
    st.markdown("---")
    st.subheader("📄 플랫폼별 맞춤형 원클릭 패키지")
    
    tab_blog1, tab_blog2 = st.tabs(["🟢 네이버 블로그 발행용 세트", "🔴 블로그스팟(구글) 발행용 세트"])
    
    with tab_blog1:
        st.text_input("📂 추천 블로그 카테고리", value=st.session_state.get("naver_category", ""))
        st.text_input("#️⃣ 복사해서 넣을 네이버 해시태그", value=st.session_state.get("naver_hashtags", ""))
        st.info("💡 네이버 블로그에 글을 복사해 붙여넣으신 후, 맨 하단에 위 해시태그를 그대로 붙여넣으세요!")

    with tab_blog2:
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.text_input("📌 검색 설명 (Meta Description)", value=st.session_state.get("meta_desc", ""))
        with col_meta2:
            st.text_input("🏷️ 라벨 (Tags)", value=st.session_state.get("blog_tags", ""))

    st.text_area("📄 본문 내용 전체 복사 (클릭 후 복사)", value=st.session_state["generated_content"], height=450)
