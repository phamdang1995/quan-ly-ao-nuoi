import json
import os
import streamlit as st

DATA_FILE = "data_ao_nuoi.json"

# Dữ liệu mặc định đầy đủ bao gồm cả phác đồ trị bệnh của dangpham
DEFAULT_DATA = {
    "users": {
        "admin": {"password": "123", "role": "admin", "name": "Phạm Hải Đăng"},
        "dangpham": {"password": "123", "role": "user", "name": "Đăng Phạm"},
    },
    "ponds": {
        "dangpham": ["Ao 1 (Thương phẩm)", "Ao 2 (Ương giống)"],
    },
    "ph_log": {},
    "huong_dan_benh": {
        "dangpham": (
            "### 1. Chuẩn Bị Trước Khi Thả:\n"
            "- Tạc vôi số lượng: **4kg / 1 ao**\n"
            "- Kết hợp: **50g thuốc tím**\n"
            "- Thời điểm: Tiến hành trước khi thả giống **5 ngày**.\n\n"
            "### 2. Tạc Vôi Định Kỳ:\n"
            "- Liều lượng vôi: **1kg / 1 ao**\n"
            "- Kết hợp: **35g Vitamin C** (khoáng riêng).\n\n"
            "### 3. Xử Lý Khi Ốc Bị Sưng Vòi (Ngâm Cấp Tốc):\n"
            "- Vớt ngay những con ốc đang có triệu chứng bệnh.\n"
            "- Cho vào thau nước sạch.\n"
            "- Hòa loãng: **5g Berberin-S** vào thau để ngâm.\n\n"
            "### 4. Tạc Thuốc Trị Bệnh Dưới Ao (Khi Sưng Vòi):\n"
            "- Dùng vi sinh: **Biobee Em (10g)**\n"
            "- Kết hợp khoáng: **Khoáng Vi lượng (100g)**\n"
            "- Cách dùng: Tạc trực tiếp xuống ao.\n\n"
            "### 5. Phòng Ngừa Bệnh Cho Ốc Qua Thức Ăn:\n"
            "- Sử dụng: **Chicocin (5g)** cho mỗi **1kg thức ăn**.\n"
            "- Cách dùng: Trộn đều với thức ăn, để nghỉ **10 phút** rồi cho ăn."
        ),
        "chuo_a": "Sổ tay phác đồ trị bệnh riêng của Chủ ao Anh Ba..."
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Đảm bảo có đủ key huong_dan_benh nếu file cũ chưa có
                if "huong_dan_benh" not in data:
                    data["huong_dan_benh"] = DEFAULT_DATA["huong_dan_benh"]
                return data
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.set_page_config(page_title="Hệ thống Quản Lý Ao Nuôi", layout="wide")

# Khởi tạo session state đăng nhập nếu chưa có
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# ----------------- GIAO DIỆN ĐĂNG NHẬP -----------------
if not st.session_state.logged_in:
    st.title("🔐 Đăng Nhập Hệ Thống Quản Lý Ao Nuôi")
    username = st.text_input("Tài khoản")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng Nhập"):
        users = data["users"]
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.session_state.name = users[username]["name"]
            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
    st.stop()

# ----------------- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP -----------------
st.sidebar.title(f"Chào, {st.session_state.name}")
if st.session_state.role == "admin":
    st.sidebar.markdown("**(Admin)**")

if st.sidebar.button("Đăng Xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.title("💧 Hệ Thống Quản Lý Ao Nuôi")

current_user = st.session_state.username
role = st.session_state.role

# 1. Phần Sổ tay hướng dẫn & Phác đồ trị bệnh
with st.expander("📖 Sổ Tay Hướng Dẫn & Phác Đồ Trị Bệnh (Tự Sửa)", expanded=True):
    if "huong_dan_benh" not in data:
        data["huong_dan_benh"] = DEFAULT_DATA["huong_dan_benh"]
    
    # Lấy nội dung hiện tại của user, nếu chưa có lấy mặc định
    current_guide = data["huong_dan_benh"].get(current_user, "")
    
    if role == "admin":
        # Admin có quyền sửa sổ tay của chính mình hoặc xem
        edited_guide = st.text_area("Chỉnh sửa nội dung phác đồ trị bệnh của bạn:", value=current_guide, height=300)
        if st.button("💾 Lưu Lại Sổ Tay"):
            data["huong_dan_benh"][current_user] = edited_guide
            save_data(data)
            st.success("Đã lưu nội dung sổ tay thành công!")
    else:
        # User thường chỉ xem hoặc tự sửa của mình
        edited_guide = st.text_area("Nội dung phác đồ trị bệnh:", value=current_guide, height=300)
        if st.button("💾 Lưu Lại Sổ Tay"):
            data["huong_dan_benh"][current_user] = edited_guide
            save_data(data)
            st.success("Đã lưu nội dung sổ tay thành công!")

# Các chức năng quản lý danh sách ao, ghi chép pH, ...
st.divider()
st.subheader("📋 Quản Lý Danh Sách Ao")
user_ponds = data["ponds"].get(current_user, [])
for p in user_ponds:
    st.markdown(f"- **{p}**")
