import streamlit as st
import google.generativeai as genai
import base64

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="GoEKT Paper Decoder",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. محرك الخطوط ---
def load_font(font_path):
    """تحميل الخط وتحويله لـ Base64"""
    try:
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

font_paths = {
    "KOLab-Bold": "fonts/KOLab-Bold.woff2",
    "KOSans-Regular": "fonts/KOSans-Regular.woff2",
    "KOSans-Bold": "fonts/KOSans-Bold.woff2",
    "KOSans-Light": "fonts/KOSans-Light.woff2"
}

font_css = ""
for name, path in font_paths.items():
    if font_b64 := load_font(path):
        family = "KO Lab" if "Lab" in name else "KO Sans"
        weight = "700" if "Bold" in name else ("300" if "Light" in name else "400")
        font_css += f"""
        @font-face {{
            font-family: '{family}';
            src: url(data:font/woff2;base64,{font_b64}) format('woff2');
            font-weight: {weight};
        }}
        """

fallback = "'KO Sans', sans-serif" if font_css else "sans-serif"
heading = "'KO Lab', sans-serif" if font_css else "sans-serif"

# --- 3. نظام التصميم ---
st.markdown(f"""
    <style>
    {font_css}

    :root {{
        --primary: #E935C1;
        --secondary: #2AB7A9;
        --dark: #0B2B40;
        --gradient: linear-gradient(135deg, #E935C1 0%, #2AB7A9 100%);
    }}

    .stApp {{
        background: var(--dark);
        font-family: {fallback};
    }}

    h1, h2, h3 {{
        font-family: {heading} !important;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        text-align: right;
    }}

    p, li, label, .stMarkdown {{
        font-family: {fallback} !important;
        color: white !important;
        text-align: right;
        direction: rtl;
    }}

    .stButton button {{
        background: var(--gradient) !important;
        color: white !important;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-family: {heading} !important;
        transition: transform 0.2s;
        width: 100%;
    }}
    .stButton button:hover {{
        transform: scale(1.02);
    }}

    .stTextArea textarea {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid var(--secondary) !important;
        color: white !important;
    }}

    .stRadio > div {{
        direction: rtl;
        text-align: right;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- 4. API Setup ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ خطأ في تحميل API Key. تأكد من إضافتها في Secrets على Streamlit Cloud.")
    st.info("للتجربة المحلية: أضف ملف .streamlit/secrets.toml وضع فيه: GEMINI_API_KEY = \"مفتاحك\"")
    st.stop()

# --- 5. دالة الترجمة ---
def goekt_translate(text, level="academic"):
    """ترجمة النصوص العلمية بمستويين"""
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

    prompts = {
        "simple": """
أنت 'GoEKT Paper Decoder - المستوى المبسط'. مهمتك: تحويل الأوراق العلمية لمحتوى سهل يفهمه أي شخص.

القواعد الصارمة:
1. **لغة بسيطة**: استخدم كلمات الحياة اليومية - بدل "التحليل الإحصائي" قل "دراسة الأرقام"
2. **أمثلة واقعية**: اشرح كل مفهوم معقد بمثال من الحياة (الطبخ، الرياضة، التسوق)
3. **جمل قصيرة**: لا تتجاوز 15 كلمة للجملة الواحدة
4. **اسأل وأجب**: استخدم أسلوب "إيه ده؟ ببساطة..." 
5. **السياق العملي**: أضف "ليه ده مهم؟ لأنه..." 
6. **تجنب المصطلحات**: إلا للضرورة القصوى (واشرحها فوراً بكلمات بسيطة)
7. **نبرة ودية**: "تخيل لو..."، "ببساطة كده..."، "يعني إيه؟"

الهدف النهائي: أي شخص عمره 16+ يقدر يفهم المحتوى بسهولة تامة.
        """,

        "academic": """
أنت 'GoEKT Paper Decoder - المستوى الأكاديمي'. مهمتك: ترجمة أكاديمية دقيقة للأوراق العلمية.

القواعد الصارمة:
1. **المصطلحات الدقيقة**: اكتب المصطلح العربي ثم الإنجليزي بين قوسين مباشرة
   مثال: الشبكات العصبية (Neural Networks)
2. **النغمة الرصينة**: لغة أكاديمية محايدة احترافية بدون عاطفة
3. **الحفاظ على البنية**: المقدمة، المنهجية، النتائج، الخلاصة كما هي
4. **الدقة المطلقة**: لا تبسط أو تختصر على حساب المعنى العلمي
5. **المراجع**: احتفظ بأي إشارات للدراسات أو الباحثين
6. **Markdown للتنسيق**: استخدم العناوين والقوائم والجداول عند الحاجة
7. **قابل للاستشهاد**: الترجمة يجب أن تكون صالحة للنشر الأكاديمي

الهدف النهائي: ترجمة يمكن نشرها في مجلة علمية عربية محكّمة.
        """
    }

    try:
        prompt = prompts[level]
        response = model.generate_content(f"{prompt}\n\nالنص الإنجليزي:\n{text}")
        return response.text
    except Exception as e:
        return f"❌ خطأ في الترجمة: {str(e)}\n\nتأكد من اتصالك بالإنترنت وصحة API Key."

# --- 6. الواجهة ---
st.markdown("# 🧬 GoEKT Paper Decoder")
st.markdown("**Empower. Knowledge. Transform.** | v2.0 Pro - نسختين للترجمة العلمية")
st.markdown("---")

col_in, col_out = st.columns([1, 1])

with col_in:
    st.markdown("### 📥 النص الإنجليزي")

    level = st.radio(
        "اختر مستوى الترجمة:",
        ("🎓 أكاديمي احترافي", "🌱 مبسط للجميع"),
        horizontal=True,
        help="الأكاديمي: للباحثين وطلاب الجامعة | المبسط: لأي شخص يريد فهم العلم"
    )

    src = st.text_area(
        "أدخل النص هنا",
        height=350,
        placeholder="الصق الورقة العلمية أو المقال البحثي هنا...",
        label_visibility="collapsed"
    )

    btn = st.button("ترجمة علمية فورية ⚡", use_container_width=True)

with col_out:
    st.markdown("### 📤 الترجمة العربية")

    if btn:
        if not src.strip():
            st.warning("⚠️ أدخل النص الإنجليزي أولاً")
        else:
            with st.spinner("🤖 جاري المعالجة بواسطة Gemini AI..."):
                mode = "simple" if "مبسط" in level else "academic"
                result = goekt_translate(src, level=mode)

                badge_color = "#2AB7A9" if mode == "simple" else "#E935C1"
                badge_text = "مستوى مبسط 🌱" if mode == "simple" else "مستوى أكاديمي 🎓"

                st.markdown(f"""
                <div style="background:{badge_color}; color:white; padding:5px 15px; 
                            border-radius:20px; display:inline-block; margin-bottom:10px;
                            font-family: {heading};">
                    {badge_text}
                </div>
                <div style="background:rgba(255,255,255,0.05); padding:20px; 
                            border-radius:10px; border-right:3px solid {badge_color};
                            text-align:right; direction:rtl; line-height:1.8;">
                {result}
                </div>
                """, unsafe_allow_html=True)

                st.success("✅ تمت الترجمة بنجاح")

                # زر التحميل
                st.download_button(
                    label="📥 تحميل الترجمة كملف نصي",
                    data=result,
                    file_name=f"goekt_translation_{mode}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#2AB7A9; font-size:14px;'>
    GoEKT Systems © 2026 | Powered by Google Gemini AI ⚡
</div>
""", unsafe_allow_html=True)
