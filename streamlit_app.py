import streamlit as st
import math
import numpy as np
from shapely.geometry import Point, MultiPoint
import os
import sys
from image_data import par_base64

#############################
# 全局参数：参数友好名称
#############################
friendly_names = {
    "h1": "扶手直径",
    "h2": "扶手高度",
    "grip": "扶手抓握区域",
    "r1": "右摆杆向前摆动限位角",
    "r2": "右摆杆向后摆动限位角",
    "r3": "左摆杆向前摆动限位角",
    "r4": "左摆杆向后摆动限位角",
    "r6": "摆杆间距",
    "p2": "踏板长度",
    "p3": "踏板宽度",
    "p5_p6": "踏板高度与护板高度",
    "p3_p4": "踏板中心间距",
    "pillar": "主立柱"
}

#############################
# 1. 页面设置与自定义 CSS
#############################
st.set_page_config(page_title="记住我的名字：梁翔(⌐■_■)", layout="wide")
# ...existing code...
# ...existing code...
custom_css_top = """
<style>
/* 隐藏 header 和 footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* 隐藏右上角的工具栏（可选） */
[data-testid="stToolbar"] {visibility: hidden;}

/* 给主内容容器增加上边距，预留顶部标题位置 */
div.block-container {
    padding-top: 80px;
}
</style>
"""
st.markdown(custom_css_top, unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] > div:first-child {
        margin-top: 0rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[role="alert"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

custom_css = """
<style>
@font-face {
    font-family: 'SimSun';
    src: url('simsun.ttc') format('truetype');
}
* {
    font-family: "SimSun", "NSimSun", "宋体", serif !important;
}
body {
    background-color: #F8F8F8;
    font-family: "SimSun", "宋体", serif;
    margin: 0;
    padding: 0;
}
h1.title-center {
    text-align: center;
    font-size: 2.5em;
    font-weight: bold;
    margin: 0;
}
h2.subtitle-center {
    text-align: left;
    font-size: 1.3em;
    color: #666;
    margin: 0;
}
/* 评估按钮全宽且悬停时字体颜色保持黑色 */
div.stButton > button {
    width: 100%;
    background-color: #FFCA28; /* 默认背景颜色 */
    color: black; /* 默认字体颜色 */
    border-radius: 8px;
    padding: 0.8em 1.8em;
    border: none;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease; /* 添加平滑过渡效果 */
}

/* 鼠标悬停时的样式 */
div.stButton > button:hover {
    background-color: #FFA000 !important; /* 悬停时背景颜色变深 */
    color: white !important; /* 悬停时字体颜色变白 */
}

/* 按钮被点击后的样式（:focus 和 :active 状态） */
div.stButton > button:focus, div.stButton > button:active {
    background-color: #FFCA28 !important; /* 点击后仍保持默认背景颜色 */
    color: black !important; /* 点击后字体颜色保持黑色 */
    outline: none; /* 去掉点击后的边框 */
}

/* 确保 :hover 优先级高于 :focus 和 :active */
div.stButton > button:focus:hover, div.stButton > button:active:hover {
    background-color: #FFA000 !important; /* 悬停时背景颜色 */
    color: white !important; /* 悬停时字体颜色 */
}
.section-title {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 0.3em;
}
hr.section-divider {
    border: 0;
    height: 1px;
    background: #ccc;
    margin: 1em 0;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ...existing code...
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100%; background-color: #F8F8F8; text-align: center; padding: 10px 0; z-index: 1000; border-bottom: 1px solid #ccc;">
  <h1 style="margin: 0; font-size:2.5em;">太空漫步机适老化评估系统</h1>
</div>
""", unsafe_allow_html=True)

custom_css_sidebar = """
<style>
[data-testid="stSidebar"] {
    background-color: #F0F2F6 !important;
}
</style>
"""
st.markdown(custom_css_sidebar, unsafe_allow_html=True)
# 在自定义 CSS 后，添加大标题及贯穿全宽的横线（放于顶端，不嵌套在列中）
#st.markdown('<h1 class="title-center">太空漫步机适老性评估系统</h1>', unsafe_allow_html=True)
#st.markdown("<hr style='border: 1px solid #ccc; width: 100%; margin: 0;'>", unsafe_allow_html=True)



#############################
# 2. 评估辅助函数
#############################
def get_region_convex_hull(h1, A, B, C, constant, num_samples=20000):
    points = []
    for _ in range(num_samples):
        alpha1 = np.random.uniform(-math.pi/3, (17/18)*math.pi)
        alpha2 = np.random.uniform(0, 0.75*math.pi)
        alpha3 = np.random.uniform(-7/18*math.pi, (4/9)*math.pi)
        x = A * math.sin(alpha1) + B * math.sin(alpha1 + alpha2) + C * math.sin(alpha1 + alpha2 - alpha3)
        y = constant - h1/2 - (A * math.cos(alpha1) + B * math.cos(alpha1 + alpha2) + C * math.cos(alpha1 + alpha2 - alpha3))
        points.append((x, y))
    return MultiPoint(points).convex_hull

def check_grip_range(h2, h3, h1):
    hull1 = get_region_convex_hull(h1, 264, 195, 79, 1159, num_samples=20000)
    hull2 = get_region_convex_hull(h1, 343, 258, 98.5, 1566.77, num_samples=20000)
    inter = hull1.intersection(hull2)
    pt = Point(h3, h2)
    return inter.contains(pt)

#############################
# 3. 各阶段评估函数（示例逻辑，可根据需要修改）
#############################
def evaluate_basic_logic(params):
    errors = []
    if not (params["h1"] > 0 and params["h1"] < 2 * params["h3"]):
         errors.append("扶手直径输入有误，请修改")
    if not (params["h2"] > 0):
         errors.append("扶手距踏板站立面垂直距离输入有误，请修改")
    if not (params["h3"] > 0):
         errors.append("扶手距踏板中心水平距离输入有误，请修改")
    for key in ["r1", "r2", "r3", "r4"]:
         if not (params[key] >= 0):
              errors.append(f"{key}（摆杆限位角）输入有误，请修改")
    if not (params["r5"] < params["c3"] - params["p5"]):
         errors.append("摆杆长度应输入有误，请修改")
    if not (params["r6"] - params["p4"] - 2 * params["p3"] > 0):
         errors.append("摆杆间距输入有误，请修改")
    if not (params["p1"] > 0 and params["p1"] < params["p3"]/2):
         errors.append("踏板圆角半径输入有误，请修改")
    if not (params["p2"] > 0):
         errors.append("踏板长度输入有误，请修改")
    if not (params["p3"] > 0):
         errors.append("踏板宽度输入有误，请修改")
    if not (params["p4"] > 0 and params["p4"] < params["r6"] - 2 * params["p3"]):
         errors.append("踏板间距输入有误，请修改")
    if not (params["p5"] > 0 and params["p5"] < params["c3"] - params["r5"]):
         errors.append("踏板底面距地面高度输入有误，请修改")
    if not (params["p6"] > 0 and params["p6"] < params["h2"]):
         errors.append("踏板护板高度输入有误，请修改")
    if not (params["p7"] > 0 and params["p7"] <= 2*(params["p2"]+params["p3"])):
         errors.append("踏板护板总长度输入有误，请修改")
    if not (params["c1"] > 0):
         errors.append("主立柱直径应输入有误，请修改")
    if not (params["c2"] > 0 and params["c2"] < params["c1"]):
         errors.append("主立柱管壁厚度输入有误，请修改")
    if not (params["c3"] > params["p5"] + params["r5"]):
         errors.append("主立柱高度输入有误，请修改")
    return errors

def evaluate_safety(params):
    errors = []
    # 扶手直径判断
    if params["h1"] < 16:
         errors.append("扶手直径过小。扶手直径应≥16mm")
    elif params["h1"] > 45:
         errors.append("扶手直径过大。扶手直径应≤45mm")
    for key, label in zip(["r1", "r2", "r3", "r4"],
                          ["右摆杆向前摆动限位角", "右摆杆向后摆动限位角", "左摆杆向前摆动限位角", "左摆杆向后摆动限位角"]):
         if not (0 < params[key] <= 65):
              errors.append(f"{label}过大。摆杆限位角应≤65°")
    if not (params["p1"] >= 3):
         errors.append("踏板圆角半径过小。踏板圆角半径应≥3mm")
    if not (params["p5"] >= 80):
         errors.append("踏板底面距地面高度过低。踏板底面距地面高度应≥80mm")
    if not (params["p6"] >= 30):
         errors.append("踏板护板高度过低。踏板护板高度应≥30mm")
    if not (params["p7"] > (4*(params["p2"]+params["p3"]))/3):
         errors.append("踏板护板总长度过小。踏板护板总长度应大于踏板周长的2/3")
    if not (params["c1"] >= 110):
         errors.append("主立柱直径过小。主立柱直径应≥110mm")
    if not (params["c2"] >= 2.75):
         errors.append("主立柱管壁厚度过薄。主立柱管壁厚度应≥2.75mm")
    return errors

def evaluate_suitability_detail(params):
    results = {}
    # 扶手部分
    results["h1"] = {}
    if params["h1"] <= 40.54:
         results["h1"]["suitability_pass"] = True
    else:
         results["h1"]["suitability_pass"] = False
         results["h1"]["suitability_msg"] = "⚠️扶手直径过大，可能无法满足部分老年人的握持需求"
    results["h2"] = {}
    if params["h2"] < 1159 - params["h1"]/2:
         results["h2"]["suitability_pass"] = True
    else:
         results["h2"]["suitability_pass"] = False
         results["h2"]["suitability_msg"] = "⚠️扶手高度过高，超过部分老年人的肩峰点高度"
    results["grip"] = {}
    if check_grip_range(params["h2"], params["h3"], params["h1"]):
         results["grip"]["suitability_pass"] = True
    else:
         results["grip"]["suitability_pass"] = False
         results["grip"]["suitability_msg"] = "⚠️扶手位置可能超出部分老年人的抓握可达范围"
    # 摆杆部分
    results["r1"] = {}
    try:
         val1 = math.degrees(math.asin((params["r5"] * math.sin(math.radians(params["r1"]))) / 800))
         results["r1"]["value"] = val1
         if val1 >= 64.1:
              results["r1"]["suitability_pass"] = True
         else:
              results["r1"]["suitability_pass"] = False
              results["r1"]["suitability_msg"] = "⚠️右侧摆杆设计可能无法满足部分老年人腿部向前摆动的运动需求"
    except Exception:
         results["r1"]["suitability_pass"] = False
         results["r1"]["suitability_msg"] = "❌右前限位角计算出错"
    results["r2"] = {}
    try:
         val2 = math.degrees(math.asin((params["r5"] * math.sin(math.radians(params["r2"]))) / 800))
         results["r2"]["value"] = val2
         if val2 >= 64.24:
              results["r2"]["suitability_pass"] = True
         else:
              results["r2"]["suitability_pass"] = False
              results["r2"]["suitability_msg"] = "⚠️右侧摆杆设计可能无法满足部分老年人腿部向后摆动的运动需求"
    except Exception:
         results["r2"]["suitability_pass"] = False
         results["r2"]["suitability_msg"] = "❌右后限位角计算出错"
    results["r3"] = {}
    try:
         val3 = math.degrees(math.asin((params["r5"] * math.sin(math.radians(params["r3"]))) / 800))
         results["r3"]["value"] = val3
         if val3 >= 55.88:
              results["r3"]["suitability_pass"] = True
         else:
              results["r3"]["suitability_pass"] = False
              results["r3"]["suitability_msg"] = "⚠️左侧摆杆设计可能无法满足部分老年人腿部向前摆动的运动需求"
    except Exception:
         results["r3"]["suitability_pass"] = False
         results["r3"]["suitability_msg"] = "❌左前限位角计算出错"
    results["r4"] = {}
    try:
         val4 = math.degrees(math.asin((params["r5"] * math.sin(math.radians(params["r4"]))) / 800))
         results["r4"]["value"] = val4
         if val4 >= 53.54:
              results["r4"]["suitability_pass"] = True
         else:
              results["r4"]["suitability_pass"] = False
              results["r4"]["suitability_msg"] = "⚠️左侧摆杆设计可能无法满足部分老年人腿部向后摆动的运动需求"
    except Exception:
         results["r4"]["suitability_pass"] = False
         results["r4"]["suitability_msg"] = "❌左后限位角计算出错"
    results["r6"] = {}
    if params["r5"] < 878:
         if params["r6"] > 437:
              results["r6"]["suitability_pass"] = True
         else:
              results["r6"]["suitability_pass"] = False
              results["r6"]["suitability_msg"] = "⚠️摆杆间距过小，可能无法满足部分老年人的身体尺寸需求"
    else:
         if params["r6"] > 625:
              results["r6"]["suitability_pass"] = True
         else:
              results["r6"]["suitability_pass"] = False
              results["r6"]["suitability_msg"] = "⚠️摆杆间距过小，可能无法满足部分老年人的身体尺寸需求"
    # 踏板部分
    results["p2"] = {}
    if params["p2"] > 302.09:
         results["p2"]["suitability_pass"] = True
    else:
         results["p2"]["suitability_pass"] = False
         results["p2"]["suitability_msg"] = "⚠️踏板长度过小，可能无法容纳部分老年人足部长度"
    results["p3"] = {}
    if params["p3"] > 129.27:
         results["p3"]["suitability_pass"] = True
    else:
         results["p3"]["suitability_pass"] = False
         results["p3"]["suitability_msg"] = "⚠️踏板宽度过小，可能无法容纳部分老年人足部宽度"
    results["p5_p6"] = {}
    if params["p5"] + params["p6"] <= 184:
         results["p5_p6"]["suitability_pass"] = True
    else:
         results["p5_p6"]["suitability_pass"] = False
         results["p5_p6"]["suitability_msg"] = "⚠️踏板加护板高度高度较高，可能超出部分老年人最大可容忍障碍物高度"
    results["p3_p4"] = {}
    if params["p3"] + params["p4"] <= 996:
         results["p3_p4"]["suitability_pass"] = True
    else:
         results["p3_p4"]["suitability_pass"] = False
         results["p3_p4"]["suitability_msg"] = "⚠️踏板中心间距过大，可能超出部分老年人两腿最大间距"
    # 主立柱部分
#    results["pillar"] = {}
#    if params["c1"] >= 110 and params["c2"] >= 2.75 and params["c3"] > params["p5"] + params["r5"]:
#         results["pillar"]["suitability_pass"] = True
#    else:
#         results["pillar"]["suitability_pass"] = False
#         results["pillar"]["suitability_msg"] = "⚠️主立柱尺寸设置有误"
    return results

def evaluate_usability_comfort_detail(params, suit_results):
    # 扶手直径 (h1)：易用性要求：30 ≤ h1 ≤ 40；舒适性要求：29.97 ≤ h1 ≤ 39.80
    if suit_results["h1"].get("suitability_pass", False):
         # 易用性判断：拆分为小于30和大于40
         if params["h1"] < 30:
              suit_results["h1"]["usability_pass"] = False
              suit_results["h1"]["usability_msg"] = "💡扶手直径较小，易用性有待提升。更大的扶手直径能够保证抓更佳的握稳定性"
         elif params["h1"] > 40:
              suit_results["h1"]["usability_pass"] = False
              suit_results["h1"]["usability_msg"] = "💡扶手直径较大，易用性有待提升。更小的扶手直径能够保证抓更佳的握稳定性"
         else:
              suit_results["h1"]["usability_pass"] = True

              
         # 舒适性判断：拆分为小于29.97和大于39.80
         if params["h1"] < 29.97:
              suit_results["h1"]["comfort_pass"] = False
              suit_results["h1"]["comfort_msg"] = "💡扶手直径较小，舒适性有待提升。更大的扶手直径舒适度更佳"
         elif params["h1"] > 39.80:
              suit_results["h1"]["comfort_pass"] = False
              suit_results["h1"]["comfort_msg"] = "💡扶手直径较大，舒适性有待提升。更小的扶手直径舒适度更佳"
         else:
              suit_results["h1"]["comfort_pass"] = True

         # 扶手高度 (h2)：易用性要求：h2 ≤ 1139
#    if suit_results["h2"].get("suitability_pass", False):
#        if params["h2"] <= 1139:
#            suit_results["h2"]["usability_pass"] = True
#        else:
#            suit_results["h2"]["usability_pass"] = False
#            suit_results["h2"]["usability_msg"] = "💡扶手高度过高，超出P5女性老年人肩峰点高度，易用性有待提升。"

    # 扶手高度 (h2)：舒适性要求：h2 ≤ 1033.2
    if suit_results["h2"].get("suitability_pass", False):
        if params["h2"] <= 1038.2:
            suit_results["h2"]["comfort_pass"] = True
        else:
            suit_results["h2"]["comfort_pass"] = False
            suit_results["h2"]["comfort_msg"] = "💡扶手高度过高，舒适性有待提升。更低的扶手高度抓握舒适度更佳（注：该舒适高度根据实验得到，实验中扶手距踏板中心水平距离d=357mm）"

    # 对 r1 单独判断（右前限位角）
    if suit_results["r1"].get("suitability_pass", False):
        val = suit_results["r1"].get("value", None)
        limit = 69.9
        if val is not None and val <= limit:
            suit_results["r1"]["usability_pass"] = True
        else:
            suit_results["r1"]["usability_pass"] = False
            suit_results["r1"]["usability_msg"] = f"💡右侧摆杆向前摆动限位角设计较大，更小的限位角度或更短的摆杆长度能够更大程度减少潜在风险"

    # 对 r2 单独判断（右后限位角）
    if suit_results["r2"].get("suitability_pass", False):
        val = suit_results["r2"].get("value", None)
        limit = 69.79
        if val is not None and val <= limit:
            suit_results["r2"]["usability_pass"] = True
        else:
            suit_results["r2"]["usability_pass"] = False
            suit_results["r2"]["usability_msg"] = f"💡右侧摆杆向后摆动限位角设计较大，更小的限位角度或更短的摆杆长度能够更大程度减少潜在风险"

    # 对 r3 单独判断（左前限位角）
    if suit_results["r3"].get("suitability_pass", False):
        val = suit_results["r3"].get("value", None)
        limit = 62.03
        if val is not None and val <= limit:
            suit_results["r3"]["usability_pass"] = True
        else:
            suit_results["r3"]["usability_pass"] = False
            suit_results["r3"]["usability_msg"] = f"💡左侧摆杆向前摆动限位角设计较大，更小的限位角度或更短的摆杆长度能够更大程度减少潜在风险"

    # 对 r4 单独判断（左后限位角）
    if suit_results["r4"].get("suitability_pass", False):
        val = suit_results["r4"].get("value", None)
        limit = 59.43
        if val is not None and val <= limit:
            suit_results["r4"]["usability_pass"] = True
        else:
            suit_results["r4"]["usability_pass"] = False
            suit_results["r4"]["usability_msg"] = f"💡左侧摆杆向后摆动限位角设计较大，更小的限位角度或更短的摆杆长度能够更大程度减少潜在风险"

    # … 其他代码
    # 踏板 p5_p6：要求：p5+p6 ≤ 150
    if suit_results["p5_p6"].get("suitability_pass", False):
         if params["p5"] + params["p6"] <= 150:
              suit_results["p5_p6"]["usability_pass"] = True
         else:
              suit_results["p5_p6"]["usability_pass"] = False
              suit_results["p5_p6"]["usability_msg"] = "💡踏板加护板高度较高，更低的高度将更符合无障碍设计原则"
    return suit_results

#############################
# 4. 页面布局与输出
#############################
# 顶部标题与旁边Logo
#col_title_left, col_title_right = st.columns([3, 1])
#with col_title_left:
#    st.markdown('<h1 class="title-center">太空漫步机适老性评估系统</h1>', unsafe_allow_html=True)
#    st.markdown("<hr style='border: 1px solid #ccc; width: 100%; margin: 0;'>", unsafe_allow_html=True)
#with col_title_right:
#    st.image("logo.png", use_container_width=True)

# 显示初始说明，直到评估按钮被点击更新
#if "evaluation_done" not in st.session_state:
#    st.session_state.evaluation_done = False

#if not st.session_state.evaluation_done:
#    st.markdown("**点击评估按钮即可开始评估。评估将从设施安全性、适用性、易用性和舒适性四个方面展开。评估结果仅针对60岁以上老年人。**")

# 三列布局：左侧示意图，中间参数输入，右侧评估结果
#col_left, col_mid, col_right = st.columns([1.2, 3, 2], gap="medium")
# 原有的三列布局代码替换为两列布局：
# 修改页面主体布局为两部分：输入（占2/3）和输出（占1/3）
col_input, col_output = st.columns([2, 1], gap="medium")

# 移除原有的左侧列示意图代码（例如：with col_left: st.markdown("### 示意图") ...）
# 改为在侧边栏中显示示意图，侧边栏默认位于页面左侧
st.sidebar.markdown("<h3 style='text-align: center;'>📐各参数示意</h3>", unsafe_allow_html=True)
# 请将下面的 par_base64 替换为你自己的图片转换后的 base64 字符串
st.sidebar.markdown(
    f'<img src="data:image/png;base64,{par_base64}" style="width:100%;">',
    unsafe_allow_html=True
)

# ...在参数输入部分
# 输入部分
with col_input:
    st.markdown("### 📃参数输入 <span style='font-size:0.8em; color:#666;'>(单位：mm ,°)</span>", unsafe_allow_html=True)
    
    # 扶手部分（3个参数，采用6列布局）
    st.markdown("""
<div style="display: flex; align-items: center;">
  <h4 style="margin: 0;">扶手</h4>
  <hr style="flex: 1; border: 1px solid #ccc; margin-left: 10px;">
</div>
""", unsafe_allow_html=True)
    row_fushou = st.columns([5,7,6,13])
    h1 = row_fushou[0].number_input("扶手直径-h1", value=40.0, step=1.0)
    h2 = row_fushou[1].number_input("扶手距踏板底面高度-h2", value=980.0, step=1.0)
    h3 = row_fushou[2].number_input("扶手水平距离-h3", value=350.0, step=1.0)
    # 剩余单元可留空

    # 摆杆部分（6个参数，整行展示）
    st.markdown("""
<div style="display: flex; align-items: center;">
  <h4 style="margin: 0;">摆杆</h4>
  <hr style="flex: 1; border: 1px solid #ccc; margin-left: 10px;">
</div>
""", unsafe_allow_html=True)
    row_basigan = st.columns(6)
    r1 = row_basigan[0].number_input("右前限位角-r1", value=62.0, step=0.1)
    r2 = row_basigan[1].number_input("右后限位角-r2", value=62.0, step=0.1)
    r3 = row_basigan[2].number_input("左前限位角-r3", value=60.0, step=0.1)
    r4 = row_basigan[3].number_input("左后限位角-r4", value=30.0, step=0.1)
    r5 = row_basigan[4].number_input("摆杆长度-r5", value=830.0, step=1.0)
    r6 = row_basigan[5].number_input("摆杆间距-r6", value=500.0, step=1.0)
    
    # 踏板部分（仅包含踏板基本参数）
    st.markdown("""
<div style="display: flex; align-items: center;">
  <h4 style="margin: 0;">踏板</h4>
  <hr style="flex: 1; border: 1px solid #ccc; margin-left: 10px;">
</div>
""", unsafe_allow_html=True)
    row_taban1 = st.columns(5)
    p1 = row_taban1[0].number_input("踏板圆角半径-p1", value=5.0, step=0.1)
    p2 = row_taban1[1].number_input("踏板长度-p2", value=350.0, step=1.0)
    p3 = row_taban1[2].number_input("踏板宽度-p3", value=150.0, step=1.0)
    p4 = row_taban1[3].number_input("踏板间距-p4", value=150.0, step=1.0)
    p5 = row_taban1[4].number_input("踏板距地面高度-p5", value=120.0, step=1.0)
    # 留空单元

    # 踏板护板部分（独立部分，仅包含两个参数）
    st.markdown("""
<div style="display: flex; align-items: center;">
  <h4 style="margin: 0;">踏板护板</h4>
  <hr style="flex: 1; border: 1px solid #ccc; margin-left: 10px;">
</div>
""", unsafe_allow_html=True)
    row_taban2 = st.columns(5)
    p6 = row_taban2[0].number_input("踏板护板高度-p6", value=40.0, step=1.0)
    p7 = row_taban2[1].number_input("踏板护板总长度-p7", value=700.0, step=1.0)
    
    # 主立柱部分（3个参数，采用6列布局）
    st.markdown("""
<div style="display: flex; align-items: center;">
  <h4 style="margin: 0;">主立柱</h4>
  <hr style="flex: 1; border: 1px solid #ccc; margin-left: 10px;">
</div>
""", unsafe_allow_html=True)
    row_pillar = st.columns(6)
    c1_val = row_pillar[0].number_input("主立柱直径-c1", value=120.0, step=1.0)
    c2_val = row_pillar[1].number_input("主立柱壁厚-c2", value=5.0, step=0.1)
    c3_val = row_pillar[2].number_input("主立柱高度-c3", value=1500.0, step=1.0)
    
    st.write("")
    btn_cols = st.columns(6)
    evaluate_button = btn_cols[2].button("评 估", key="evaluate_btn")

# 输出部分（保持原有代码不变）
with col_output:
    st.markdown("### 👁️‍🗨️评估结果")
    st.markdown(
        "<p style='font-size:16px; margin-bottom:20px;'>点击评估按钮即可开始评估。评估将从设施安全性、适用性、易用性和舒适性四个方面展开。评估结果仅针对60岁以上老年人。</p>",
        unsafe_allow_html=True
    )

#############################
# 6. 评估流程（仅当点击评估按钮时更新结果）
#############################
if evaluate_button:
    st.session_state.evaluation_done = True
    params = {
        "h1": h1, "h2": h2, "h3": h3,
        "r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5, "r6": r6,
        "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "p6": p6, "p7": p7,
        "c1": c1_val, "c2": c2_val, "c3": c3_val
    }
    
    with col_output:
        # 基本逻辑评估
        basic_errors = evaluate_basic_logic(params)
        if basic_errors:
            for err in basic_errors:
                st.error(err)
            st.stop()
        
        # 安全性评估
        safety_errors = evaluate_safety(params)
        if safety_errors:
            st.markdown("<p style='font-size:18px;'>🚨设施参数设计不符合安全性标准</p>", unsafe_allow_html=True)
            for err in safety_errors:
                st.error(err)
            st.stop()
        else:
            st.success("✅设施符合安全性标准")
        
        st.markdown("<hr class='section-divider' style='height:1px; border:none; background:#ccc; margin:0;'>", unsafe_allow_html=True)
        
        # 适用性评估
        suit_results = evaluate_suitability_detail(params)
        suit_results = evaluate_usability_comfort_detail(params, suit_results)
        
        groups = {
            "扶手": ["h1", "h2", "grip"],
            "摆杆": ["r1", "r2", "r3", "r4", "r6"],
            "踏板": ["p2", "p3", "p5_p6", "p3_p4"],
#            "主立柱": ["pillar"]
        }
        # 主立柱部分单独判断
#        if params["c1"] >= 110 and params["c2"] >= 2.75 and params["c3"] > params["p5"] + params["r5"]:
#            suit_results["pillar"] = {"suitability_pass": True}
#        else:
#            suit_results["pillar"] = {"suitability_pass": False, "suitability_msg": "主立柱应满足直径≥110mm、管壁厚度≥2.75mm，且高度>踏板底面高度+摆杆长度"}
        
        for comp, keys in groups.items():
            comp_pass = all(suit_results.get(key, {}).get("suitability_pass", False) for key in keys)
            if comp_pass:
                st.markdown(f"<p style='font-size:18px;'>✅{comp}部分适用性良好</p>", unsafe_allow_html=True)
            else:
                for key in keys:
                    if key in suit_results and not suit_results[key].get("suitability_pass", False):
                        st.warning(f"{suit_results[key].get('suitability_msg')}")
        
        st.markdown("<hr class='section-divider' style='height:1px; border:none; background:#ccc; margin:0;'>", unsafe_allow_html=True)

        # 舒适性评估（仅适用性通过的参数）
        for key, result in suit_results.items():
            if result.get("suitability_pass", False) and "comfort_pass" in result:
                if result["comfort_pass"]:
                    st.markdown(f"<p style='font-size:18px;'>✅{friendly_names.get(key, key)}使用舒适</p>", unsafe_allow_html=True)
                else:
                    st.info(f"{result.get('comfort_msg')}")

        st.markdown("<hr class='section-divider' style='height:1px; border:none; background:#ccc; margin:0;'>", unsafe_allow_html=True)
        
        # 易用性评估（仅适用性通过的参数）
        for key, result in suit_results.items():
            if result.get("suitability_pass", False) and "usability_pass" in result:
                if result["usability_pass"]:
                    st.markdown(f"<p style='font-size:18px;'>✅{friendly_names.get(key, key)}-易用性良好</p>", unsafe_allow_html=True)
                else:
                    st.info(f"{result.get('usability_msg')}")
        
