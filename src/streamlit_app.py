import streamlit as st
from openai import OpenAI
import os
from datetime import datetime, timedelta
import glob
import numpy as np
import random
import base64

# 页面配置
st.set_page_config(
    page_title="八字塔罗运势",
    page_icon="🔮",
    layout="centered"
)

# -------------------- 背景视频功能 --------------------
def set_background_video(video_path):
    """设置背景视频"""
    try:
        # 读取视频文件并编码为base64
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode()
        
        # 创建背景视频的HTML/CSS
        background_video_html = f"""
        <style>
        #bgVideo {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            z-index: -100;
            background-size: cover;
        }}
        
        /* 确保Streamlit内容在视频之上 */
        .main {{
            position: relative;
            z-index: 1;
        }}
        
        .block-container {{
            position: relative;
            z-index: 2;
        }}
        
        /* 生肖动图样式 */
        .zodiac-video {{
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            width: 100%;
            max-height: 300px;
            object-fit: cover;
        }}
        </style>
        <video id="bgVideo" autoplay muted loop>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            您的浏览器不支持视频标签。
        </video>
        """
        st.markdown(background_video_html, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.warning(f"背景视频加载失败: {e}")
        return False

def setup_background_video():
    """设置背景视频"""
    # 搜索视频文件 - 根据您的项目结构调整路径
    video_dirs = ["src/videos", "videos", "./src/videos", "./videos"]
    video_extensions = ("*.mp4", "*.MP4", "*.mov", "*.MOV")
    
    video_files = []
    for video_dir in video_dirs:
        if os.path.exists(video_dir):
            for ext in video_extensions:
                found_videos = glob.glob(os.path.join(video_dir, ext))
                video_files.extend(found_videos)
    
    # 如果找到视频文件，选择第一个
    if video_files:
        video_path = video_files[0]
        return set_background_video(video_path)
    else:
        # 如果没有找到视频，使用备用方案
        st.markdown("""
        <style>
        .main {
            background: linear-gradient(125deg, #0f0c29, #302b63, #24243e);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        </style>
        """, unsafe_allow_html=True)
        return False

# -------------------- 简化样式 --------------------
def set_simple_style():
    st.markdown("""
    <style>
        .main { 
            background-color: transparent;
        }
        
        .block-container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem;
            backdrop-filter: blur(5px);
        }
        
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: bold;
            margin: 0.2rem;
        }
        
        .recommendation-button {
            background-color: #6c5ce7;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            font-weight: bold;
            margin: 0.3rem;
            width: 100%;
            text-align: center;
        }
        
        .recommendation-button:hover {
            background-color: #5b4bc4;
        }
        
        .active-button {
            background-color: #e17055 !important;
        }
        
        .disclaimer {
            background-color: rgba(255, 243, 205, 0.9);
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: #856404;
        }
        
        .zodiac-section {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        }
        
        .guardian-spirit {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.9) 0%, rgba(255, 165, 0, 0.9) 100%);
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        }
        
        .recommendation-card {
            background-color: rgba(255, 255, 255, 0.95);
            border: 2px solid #6c5ce7;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            background-color: rgba(255, 255, 255, 0.9);
        }
        
        .user-message {
            background-color: rgba(227, 242, 253, 0.9);
            border-left: 4px solid #2196f3;
        }
        
        .assistant-message {
            background-color: rgba(243, 229, 245, 0.9);
            border-left: 4px solid #9c27b0;
        }
        
        /* 视频容器样式 */
        .video-container {
            position: relative;
            width: 100%;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

set_simple_style()

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-72997944466a4af2bcd52a068895f8cf",
    base_url="https://api.deepseek.com"
)

# -------------------- 会话状态初始化 --------------------
def init_session_state():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "birth_info" not in st.session_state:
        st.session_state.birth_info = None
    if "daily_fortune" not in st.session_state:
        st.session_state.daily_fortune = None
    if "media_indexed" not in st.session_state:
        st.session_state.media_indexed = False
    if "songs_meta" not in st.session_state:
        st.session_state.songs_meta = []
    if "all_images" not in st.session_state:
        st.session_state.all_images = []
    if "zodiac_videos" not in st.session_state:  # 改为存储视频
        st.session_state.zodiac_videos = {}
    if "last_fortune_date" not in st.session_state:
        st.session_state.last_fortune_date = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    if "background_video" not in st.session_state:
        st.session_state.background_video = None
    # 个性推荐相关状态
    if "current_recommendation" not in st.session_state:
        st.session_state.current_recommendation = None
    if "recommendation_type" not in st.session_state:
        st.session_state.recommendation_type = None
    if "personal_recommendations" not in st.session_state:
        st.session_state.personal_recommendations = {}

init_session_state()

# -------------------- 核心工具函数 --------------------
ZODIAC = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
ZODIAC_EMOJIS = ["🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑", "🐵", "🐔", "🐶", "🐷"]
ZODIAC_DESCRIPTIONS = {
    "鼠": "聪明机智，适应力强", "牛": "勤奋踏实，稳重可靠", "虎": "勇敢果断，充满活力",
    "兔": "温和优雅，心思细腻", "龙": "自信强大，领导力强", "蛇": "智慧深沉，直觉敏锐",
    "马": "自由奔放，热情开朗", "羊": "温和善良，富有同情心", "猴": "聪明伶俐，善于交际",
    "鸡": "勤奋守时，注重细节", "狗": "忠诚可靠，正义感强", "猪": "真诚坦率，福气满满"
}

GUARDIAN_SPIRITS = {
    "鼠": "智慧守护灵 - 赐予你敏锐的洞察力和应变能力",
    "牛": "坚韧守护灵 - 赋予你持久的耐力和坚定的意志",
    "虎": "勇气守护灵 - 带给你无畏的勇气和行动力",
    "兔": "温柔守护灵 - 守护你的善良和细腻情感",
    "龙": "力量守护灵 - 赐予你强大的领导力和创造力",
    "蛇": "智慧守护灵 - 赋予你深刻的直觉和洞察力",
    "马": "自由守护灵 - 带给你奔放的活力和冒险精神",
    "羊": "和谐守护灵 - 守护你的温柔和艺术天赋",
    "猴": "机智守护灵 - 赐予你灵活的思维和沟通能力",
    "鸡": "精准守护灵 - 赋予你细致入微的观察力",
    "狗": "忠诚守护灵 - 守护你的真诚和正义感",
    "猪": "福气守护灵 - 带给你好运和丰盛的能量"
}

def year_to_zodiac(year: int):
    return ZODIAC[(year - 1900) % 12]

def get_zodiac_emoji(zodiac: str):
    index = ZODIAC.index(zodiac)
    return ZODIAC_EMOJIS[index]

def get_zodiac_description(zodiac: str):
    return ZODIAC_DESCRIPTIONS.get(zodiac, "")

def get_guardian_spirit(zodiac: str):
    return GUARDIAN_SPIRITS.get(zodiac, "")

def load_media_resources():
    """加载音乐和视频资源 - 根据您的项目结构调整路径"""
    try:
        songs = []
        all_images = []
        zodiac_videos = {}  # 改为存储视频

        # 加载音乐 - 从 src/music/ 目录
        music_dirs = ["src/music", "./src/music", "music", "./music"]
        for music_dir in music_dirs:
            if os.path.exists(music_dir):
                for ext in ("*.mp3", "*.wav", "*.m4a"):
                    music_files = glob.glob(os.path.join(music_dir, "**", ext), recursive=True)
                    for p in music_files:
                        if os.path.isfile(p):
                            fname = os.path.basename(p)
                            name_no_ext = os.path.splitext(fname)[0]
                            # 简单的文件名解析
                            if " - " in name_no_ext:
                                parts = name_no_ext.split(" - ")
                                title = parts[-1]
                                emotion = parts[0] if len(parts) > 1 else "中性"
                            else:
                                title = name_no_ext
                                emotion = "中性"
                            
                            songs.append({
                                "filename": fname,
                                "title": title,
                                "emotion": emotion,
                                "path": p
                            })

        # 加载图片和视频 - 从 src/images/ 目录
        image_dirs = ["src/images", "./src/images", "images", "./images"]
        for image_dir in image_dirs:
            if os.path.exists(image_dir):
                # 加载静态图片
                for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                    image_files = glob.glob(os.path.join(image_dir, "**", ext), recursive=True)
                    for p in image_files:
                        if os.path.isfile(p):
                            all_images.append(p)
                
                # 加载生肖动图 (mp4格式)
                for ext in ("*.mp4", "*.MP4", "*.mov", "*.MOV"):
                    video_files = glob.glob(os.path.join(image_dir, "**", ext), recursive=True)
                    for p in video_files:
                        if os.path.isfile(p):
                            filename = os.path.basename(p).lower()
                            for zodiac in ZODIAC:
                                if zodiac in filename:
                                    zodiac_videos[zodiac] = p
                                    break

        st.session_state.songs_meta = songs
        st.session_state.all_images = all_images
        st.session_state.zodiac_videos = zodiac_videos  # 改为存储视频
        st.session_state.media_indexed = True
        
        st.success(f"✅ 加载了 {len(songs)} 首音乐, {len(all_images)} 张图片和 {len(zodiac_videos)} 个生肖动图")
        
    except Exception as e:
        st.error(f"加载媒体资源时出错: {e}")

def match_song_by_text(text: str, top_k=1):
    """简化版音乐匹配"""
    songs = st.session_state.songs_meta
    if not songs:
        return []

    text_lower = text.lower()
    matched_songs = []
    
    emotion_keywords = {
        "快乐": ["快乐", "开心", "喜悦", "幸福", "愉快", "高兴", "好运", "顺利"],
        "悲伤": ["悲伤", "难过", "伤心", "忧郁", "失落", "困难", "挫折"],
        "平静": ["平静", "安宁", "安静", "平和", "稳定", "放松", "休息"],
        "振奋": ["振奋", "兴奋", "激动", "热情", "活力", "充满", "积极"]
    }
    
    for song in songs:
        score = 0
        song_emotion = song['emotion']
        song_title = song['title'].lower()
        
        # 基于情感标签匹配
        for emotion, keywords in emotion_keywords.items():
            if emotion in song_emotion:
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 2
                        break
        
        # 基于标题关键词匹配
        title_words = song_title.split()
        for word in title_words:
            if len(word) > 2 and word in text_lower:
                score += 1
        
        if score > 0:
            matched_songs.append((score, song))
    
    if not matched_songs and songs:
        # 如果没有匹配的，随机选择一首
        matched_songs.append((1, random.choice(songs)))
    
    matched_songs.sort(key=lambda x: x[0], reverse=True)
    return matched_songs[:top_k]

def get_random_image():
    all_images = st.session_state.all_images
    if all_images:
        return random.choice(all_images)
    return None

def get_zodiac_video(zodiac):
    """获取生肖动图"""
    zodiac_videos = st.session_state.zodiac_videos
    return zodiac_videos.get(zodiac)

def display_zodiac_video(video_path, zodiac):
    """显示生肖动图"""
    if video_path and os.path.exists(video_path):
        try:
            # 读取视频文件
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
            
            # 显示视频
            st.video(video_bytes)
            
        except Exception as e:
            st.error(f"加载生肖动图失败: {e}")
            # 备用方案：显示随机图片
            random_image = get_random_image()
            if random_image and os.path.exists(random_image):
                st.image(random_image, caption=f"今日守护生肖：{zodiac}", use_container_width=True)
    else:
        # 如果没有找到动图，显示随机图片
        random_image = get_random_image()
        if random_image and os.path.exists(random_image):
            st.image(random_image, caption=f"今日守护生肖：{zodiac}", use_container_width=True)
        else:
            st.info("📷 暂无生肖动图资源")

def display_media(song_meta, zodiac):
    """显示动图和音乐"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        zodiac_video = get_zodiac_video(zodiac)
        if zodiac_video:
            st.markdown(f"<div class='video-container'>", unsafe_allow_html=True)
            display_zodiac_video(zodiac_video, zodiac)
            st.markdown(f"</div>", unsafe_allow_html=True)
            st.caption(f"今日守护生肖：{zodiac}")
        else:
            random_image = get_random_image()
            if random_image and os.path.exists(random_image):
                st.image(random_image, caption=f"今日守护生肖：{zodiac}", use_container_width=True)
            else:
                st.info("📷 暂无生肖动图资源")
    
    with col2:
        st.subheader(f"🎵 {song_meta['title']}")
        st.write(f"**情感标签：** {song_meta['emotion']}")
        
        if os.path.exists(song_meta["path"]):
            try:
                st.audio(song_meta["path"])
            except Exception as e:
                st.error(f"播放音乐失败: {e}")
        else:
            st.error("音乐文件不存在")

def generate_specific_recommendation(recommendation_type, zodiac, birth_year, place, birth_hour, gender):
    """生成特定类型的推荐"""
    prompts = {
        "工作类型": f"基于生肖{zodiac}、{birth_year}年出生、{place}人、{gender}性的特点，推荐3个最适合的工作类型，并说明理由",
        "车型": f"根据生肖{zodiac}的性格特点和命理，推荐2款最适合的汽车类型，说明为什么适合",
        "工作方位": f"基于八字命理，为生肖{zodiac}的{gender}性推荐2个最吉利的工作和发展方位",
        "饮食": f"根据生肖{zodiac}的体质特点，推荐适合的饮食习惯和3种有益食物",
        "家具布局": f"为生肖{zodiac}的{gender}性提供3条家居风水布局建议",
        "运动": f"推荐3种最适合生肖{zodiac}的{gender}性参与的运动锻炼方式",
        "花草绿植": f"推荐3种最适合生肖{zodiac}养护的植物，说明其风水作用",
        "电影": f"推荐2部最适合生肖{zodiac}的{gender}性观看的电影，并说明推荐理由"
    }
    
    prompt = prompts.get(recommendation_type, "")
    if not prompt:
        return "暂无该类型的推荐信息"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"暂时无法生成{recommendation_type}推荐，请稍后再试。"

def should_regenerate_fortune():
    """检查是否需要重新生成运势"""
    today = datetime.now().date()
    if st.session_state.last_fortune_date != today:
        st.session_state.last_fortune_date = today
        st.session_state.daily_fortune = None
        return True
    return False

def chat_with_ai(user_message, birth_info, zodiac):
    """与AI聊天"""
    if not birth_info:
        return "请先在主页输入您的八字信息。"
    
    prompt = f"""
    用户信息：
    - 生肖：{zodiac}
    - 出生年份：{birth_info['year']}
    - 出生地点：{birth_info['place']}
    - 出生时辰：{birth_info['hour']}
    - 性别：{birth_info['gender']}
    
    用户问题：{user_message}
    
    请基于用户的八字信息和生肖特点，给出专业、温暖的回答。
    回答要结合传统命理智慧，同时保持积极正向。
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "抱歉，我现在无法回答您的问题。请稍后再试。"

def render_chat_interface():
    """显示聊天界面"""
    st.subheader("💬 您还有什么想了解的吗？")
    st.write("我可以为您解答关于运势、命理、生活建议等任何问题")
    
    # 显示聊天历史
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 您：</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🔮 运势助手：</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # 聊天输入
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.text_input(
            "输入您的问题...",
            value=st.session_state.user_question,
            key="chat_input",
            placeholder="例如：我的财运如何？感情运势怎么样？健康方面要注意什么？"
        )
    with col2:
        send_button = st.button("发送", use_container_width=True)
    
    if send_button and user_question.strip():
        # 添加用户消息到历史
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # 获取AI回复
        with st.spinner("🔮 正在思考..."):
            birth_info = st.session_state.birth_info
            zodiac = year_to_zodiac(birth_info['year']) if birth_info else "未知"
            ai_response = chat_with_ai(user_question, birth_info, zodiac)
            
            # 添加AI回复到历史
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_response
            })
        
        # 清空输入框
        st.session_state.user_question = ""
        st.rerun()

# -------------------- 页面组件 --------------------
def render_home_page():
    st.title("🔮 八字塔罗运势")
    st.subheader("✨ 输入您的八字信息，探索专属运势")

    if not st.session_state.media_indexed:
        with st.spinner("📂 加载媒体资源..."):
            load_media_resources()

    with st.form("birth_info_form"):
        st.subheader("📝 请输入您的八字信息")
        
        col1, col2 = st.columns(2)
        with col1:
            birth_year = st.number_input("出生年份", min_value=1900, max_value=datetime.now().year, value=2000)
            birth_month = st.number_input("出生月份", min_value=1, max_value=12, value=1)
        with col2:
            birth_day = st.number_input("出生日期", min_value=1, max_value=31, value=1)
            birth_hour = st.selectbox("出生时辰", [
                "子时(23-1)", "丑时(1-3)", "寅时(3-5)", "卯时(5-7)", 
                "辰时(7-9)", "巳时(9-11)", "午时(11-13)", "未时(13-15)",
                "申时(15-17)", "酉时(17-19)", "戌时(19-21)", "亥时(21-23)"
            ], index=4)
        
        col3, col4 = st.columns(2)
        with col3:
            birth_place = st.text_input("出生地点", placeholder="例如：北京、上海")
        with col4:
            gender = st.selectbox("性别", options=["男", "女"])
        
        submit_btn = st.form_submit_button("🚀 保存八字信息", type="primary")
        
        if submit_btn:
            if birth_place.strip() == "":
                st.warning("请输入出生地点")
            else:
                st.session_state.birth_info = {
                    "year": birth_year, "month": birth_month, "day": birth_day,
                    "hour": birth_hour, "place": birth_place, "gender": gender
                }
                st.success("✅ 八字信息已保存！")
                # 重置状态
                st.session_state.daily_fortune = None
                st.session_state.personal_recommendations = {}
                st.session_state.chat_history = []

    # 显示生肖信息
    if st.session_state.birth_info:
        st.divider()
        zodiac = year_to_zodiac(st.session_state.birth_info['year'])
        zodiac_emoji = get_zodiac_emoji(zodiac)
        zodiac_desc = get_zodiac_description(zodiac)
        
        st.markdown(f"""
        <div class="zodiac-section">
            <h1>{zodiac_emoji} {zodiac}</h1>
            <h3>{zodiac_desc}</h3>
            <p>出生年份：{st.session_state.birth_info['year']}年 | 生肖：{zodiac} | 性别：{st.session_state.birth_info['gender']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 导航到其他页面
        st.divider()
        st.subheader("探索更多")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 查看今日运势", use_container_width=True):
                st.session_state.current_page = "daily"
                st.rerun()
        with col2:
            if st.button("🌟 查看个性推荐", use_container_width=True):
                st.session_state.current_page = "personal"
                st.rerun()
    else:
        st.info("👆 请先输入您的八字信息以解锁完整功能")

def render_daily_fortune():
    st.title("📅 今日运势")
    
    if not st.session_state.birth_info:
        st.warning("请先在主页面输入八字信息")
        if st.button("返回主页"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    birth_info = st.session_state.birth_info
    zodiac = year_to_zodiac(birth_info['year'])
    
    st.subheader(f"🐉 您的生肖：{zodiac}")
    st.write(f"**出生信息：** {birth_info['year']}年{birth_info['month']}月{birth_info['day']}日 {birth_info['hour']} | {birth_info['place']} | 性别：{birth_info['gender']}")
    st.divider()

    # 检查是否需要重新生成运势
    should_regenerate_fortune()

    # 个人生肖守护灵
    st.subheader("✨ 个人生肖守护灵")
    guardian_spirit = get_guardian_spirit(zodiac)
    st.markdown(f"""
    <div class="guardian-spirit">
        <h3>🌟 {guardian_spirit.split(' - ')[0]} 🌟</h3>
        <p>{guardian_spirit.split(' - ')[1]}</p>
    </div>
    """, unsafe_allow_html=True)

    # 今日运势
    st.subheader("🎯 今日运势")
    if st.session_state.daily_fortune is None:
        with st.spinner("🔮 正在占卜今日运势..."):
            try:
                prompt = f"""
                用户生肖：{zodiac}
                出生年份：{birth_info['year']}
                出生地点：{birth_info['place']}
                性别：{birth_info['gender']}
                当前日期：{datetime.now().strftime('%Y年%m月%d日')}
                
                生成简短精准的今日运势（60字左右），包含：
                1. 整体运势走向
                2. 核心注意事项
                3. 积极正向的祝福结尾
                语言温暖、简洁。
                """

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                st.session_state.daily_fortune = response.choices[0].message.content.strip()
            except Exception as e:
                st.session_state.daily_fortune = "今日运势平稳，保持积极心态，好事自然来。注意与人沟通，避免小误会。祝你今天一切顺利！"

    st.info(st.session_state.daily_fortune)

    # 音乐推荐
    st.subheader("🎶 今日守护音乐")
    if st.session_state.songs_meta:
        matched_songs = match_song_by_text(st.session_state.daily_fortune, 1)
        if matched_songs:
            score, song = matched_songs[0]
            display_media(song, zodiac)
        else:
            st.warning("暂无匹配的音乐推荐")
    else:
        st.info("🎵 音乐功能准备中...")

    # 免责声明
    st.markdown("""
    <div class="disclaimer">
    💫 以上内容仅供参考，八字可以更深度的了解自己，但生活是不可被定义的。
    </div>
    """, unsafe_allow_html=True)

    # 聊天界面
    st.divider()
    render_chat_interface()

    # 返回主页
    st.divider()
    if st.button("🔙 返回主页"):
        st.session_state.current_page = "home"
        st.rerun()

def render_personal_recommendation():
    st.title("🌟 个性推荐")
    st.subheader("基于您的八字生成的专属生活建议")
    
    if not st.session_state.birth_info:
        st.warning("请先在主页面输入八字信息")
        if st.button("返回主页"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    birth_info = st.session_state.birth_info
    zodiac = year_to_zodiac(birth_info['year'])
    
    st.write(f"**您的生肖：** {zodiac}")
    st.write(f"**出生年份：** {birth_info['year']}年")
    st.write(f"**出生地点：** {birth_info['place']}")
    st.write(f"**出生时辰：** {birth_info['hour']}")
    st.write(f"**性别：** {birth_info['gender']}")
    
    st.divider()
    
    # 推荐类型按钮
    st.subheader("🎯 选择推荐类型")
    
    recommendation_types = {
        "💼 工作类型": "工作类型",
        "🚗 车型推荐": "车型", 
        "🧭 工作方位": "工作方位",
        "🍽️ 饮食建议": "饮食",
        "🏠 家具布局": "家具布局",
        "🏃 运动推荐": "运动",
        "🌿 花草绿植": "花草绿植",
        "🎬 电影推荐": "电影"
    }
    
    # 创建按钮网格
    cols = st.columns(4)
    for idx, (display_name, rec_type) in enumerate(recommendation_types.items()):
        with cols[idx % 4]:
            is_active = st.session_state.recommendation_type == rec_type
            button_style = "active-button" if is_active else ""
            if st.button(display_name, use_container_width=True, key=f"btn_{rec_type}"):
                st.session_state.recommendation_type = rec_type
                st.session_state.current_recommendation = None
                st.rerun()
    
    st.divider()
    
    # 显示选中的推荐内容
    if st.session_state.recommendation_type:
        st.subheader(f"📋 {[k for k, v in recommendation_types.items() if v == st.session_state.recommendation_type][0]}")
        
        # 检查是否已经生成过该推荐
        if st.session_state.recommendation_type in st.session_state.personal_recommendations:
            recommendation_content = st.session_state.personal_recommendations[st.session_state.recommendation_type]
        else:
            # 生成新的推荐
            with st.spinner(f"🔮 正在生成{st.session_state.recommendation_type}推荐..."):
                recommendation_content = generate_specific_recommendation(
                    st.session_state.recommendation_type,
                    zodiac, birth_info['year'], birth_info['place'], 
                    birth_info['hour'], birth_info['gender']
                )
                # 保存到session state
                st.session_state.personal_recommendations[st.session_state.recommendation_type] = recommendation_content
        
        # 显示推荐内容
        st.markdown(f"""
        <div class="recommendation-card">
            {recommendation_content}
        </div>
        """, unsafe_allow_html=True)
        
        # 重新生成按钮
        if st.button("🔄 重新生成此推荐", use_container_width=True):
            with st.spinner("重新生成中..."):
                new_recommendation = generate_specific_recommendation(
                    st.session_state.recommendation_type,
                    zodiac, birth_info['year'], birth_info['place'],
                    birth_info['hour'], birth_info['gender']
                )
                st.session_state.personal_recommendations[st.session_state.recommendation_type] = new_recommendation
            st.rerun()
    else:
        st.info("👆 请选择上方的推荐类型来查看具体建议")
    
    # 免责声明
    st.markdown("""
    <div class="disclaimer">
    💫 以上内容仅供参考，八字可以更深度的了解自己，但生活是不可被定义的。
    </div>
    """, unsafe_allow_html=True)

    # 聊天界面
    st.divider()
    render_chat_interface()

    # 返回主页
    st.divider()
    if st.button("🔙 返回主页"):
        st.session_state.current_page = "home"
        st.rerun()

# -------------------- 主程序入口 --------------------
def main():
    # 设置背景视频
    if st.session_state.background_video is None:
        setup_background_video()
    
    # 页面路由
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "daily":
        render_daily_fortune()
    elif st.session_state.current_page == "personal":
        render_personal_recommendation()

if __name__ == "__main__":
    main()
