import json
import os
from datetime import datetime
import streamlit as st

DATA_FILE = "data_ao_nuoi.json"

DEFAULT_DATA = {
    "users": {
        "admin": {"password": "123", "role": "admin", "ten": "Phạm Hải Đăng"},
        "dangpham": {"password": "123", "role": "user", "ten": "Đăng Phạm"},
        "chuo_a": {"password": "123", "role": "user", "ten": "Anh Ba"}
    },
    "ponds": {
        "dangpham": ["Ao 1 (Thương phẩm)", "Ao 2 (Ương giống)"],
        "chuo_a": ["Ao Ba 1", "Ao Ba 2"]
    },
    "ph_log": {}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.set_page_config(page_title="Hệ thống Quản Lý Ao Nuôi", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.ten = ""

# ----------------- GIAO DIỆN ĐĂNG NHẬP -----------------
if not st.session_state.logged_in:
    st.title("🔐 Đăng Nhập Hệ Thống Quản Lý Ao Nuôi")
    username = st.text_input("Tài khoản")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng Nhập"):
        users = data.get("users", {})
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username].get("role", "user")
            st.session_state.ten = users[username].get("ten", username)
            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
    st.stop()

# ----------------- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP -----------------
st.sidebar.title(f"Chào, {st.session_state.ten}")
if st.session_state.role == "admin":
    st.sidebar.markdown("**(Admin)**")

if st.sidebar.button("Đăng Xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.ten = ""
    st.rerun()

st.title("💧 Hệ Thống Quản Lý Ao Nuôi")

current_user = st.session_state.username

# 1. Sổ Tay Hướng Dẫn & Phác Đồ Trị Bệnh (Cố định, không cho sửa)
with st.expander("📖 Sổ Tay Hướng Dẫn & Phác Đồ Trị Bệnh (Cố Định)", expanded=True):
    st.markdown("""
### 1. Chuẩn Bị Trước Khi Thả:
- Tạc vôi số lượng: **4kg / 1 ao**
- Kết hợp: **50g thuốc tím**
- Thời điểm: Tiến hành trước khi thả giống **5 ngày**.

### 2. Tạc Vôi Định Kỳ:
- Liều lượng vôi: **1kg / 1 ao**
- Kết hợp: **35g Vitamin C** (khoáng riêng).

### 3. Xử Lý Khi Ốc Bị Sưng Vòi (Ngâm Cấp Tốc):
- Vớt ngay những con ốc đang có triệu chứng bệnh.
- Cho vào thau nước sạch.
- Hòa loãng: **5g Berberin-S** vào thau để ngâm.

### 4. Tạc Thuốc Trị Bệnh Dưới Ao (Khi Sưng Vòi):
- Dùng vi sinh: **Biobee Em (10g)**
- Kết hợp khoáng: **Khoáng Vi lượng (100g)**
- Cách dùng: Tạc trực tiếp xuống ao.

### 5. Phòng Ngừa Bệnh Cho Ốc Qua Thức Ăn:
- Sử dụng: **Chicocin (5g)** cho mỗi **1kg thức ăn**.
- Cách dùng: Trộn đều với thức ăn, để nghỉ **10 phút** rồi cho ăn.
    """)

st.divider()

# 2. Quản Lý Danh Sách Ao Của Cả Chủ Ao Khác
st.subheader("👥 Quản Lý Danh Sách Tài Khoản & Xem Ao Của Chủ Khác")

all_users = data.get("users", {})
user_options = {info.get("ten", uname): uname for uname, info in all_users.items()}
selected_name = st.selectbox("Lọc xem ao theo chủ sở hữu:", list(user_options.keys()))
selected_username = user_options[selected_name]

st.markdown(f"**Danh sách ao của chủ ao: {selected_name}**")

# Hỗ trợ cấu trúc cũ hoặc cấu trúc mới của file json
ponds_data = data.get("ponds", {})
selected_user_ponds = []
if isinstance(ponds_data, dict):
    selected_user_ponds = ponds_data.get(selected_username, [])
elif isinstance(ponds_data, list):
    # Nếu trong json lưu danh sách theo dạng mảng data_ao
    selected_user_ponds = [item.get("ten") for item in ponds_data if item.get("chu_so_huu") == selected_username]

if selected_user_ponds:
    for p in selected_user_ponds:
        st.markdown(f"- 🌊 {p}")
else:
    st.info("Chủ ao này chưa có ao nào.")

st.divider()

# 3. Ghi Chép pH (Tự động cập nhật ngày giờ hiện tại, không cần sửa)
st.subheader("📊 Ghi Nhập & Theo Dõi Chỉ Số pH")

if selected_user_ponds:
    selected_pond = st.selectbox("Chọn ao cần đo:", selected_user_ponds)
    ph_value = st.number_input("Nhập giá trị pH:", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.info(f"🕒 Thời gian ghi nhận tự động: **{current_time_str}**")
    
    if st.button("💾 Lưu pH"):
        if "ph_log" not in data:
            data["ph_log"] = {}
        if current_user not in data["ph_log"]:
            data["ph_log"][current_user] = {}
        if selected_pond not in data["ph_log"][current_user]:
            data["ph_log"][current_user][selected_pond] = []
            
        data["ph_log"][current_user][selected_pond].append({
            "time": current_time_str,
            "ph": ph_value
        })
        save_data(data)
        st.success("Đã lưu chỉ số pH thành công!")

    if current_user in data["ph_log"] and selected_pond in data["ph_log"][current_user]:
        st.markdown("##### Lịch sử đo pH của ao này:")
        logs = data["ph_log"][current_user][selected_pond]
        for log in reversed(logs):
            st.text(f"- Thời gian: {log['time']} | pH: {log['ph']}")
else:
    st.warning("Bạn chưa có ao nào trong hệ thống để ghi nhận pH.")
