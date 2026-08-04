from datetime import datetime, timedelta
import json
import os
import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Quản Lý Ao Nuôi", page_icon="💧", layout="centered"
)

DATA_FILE = "data_ao_nuoi.json"


# --- HÀM ĐỌC / GHI DỮ LIỆU ---
def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for ao in data.get("data_ao", []):
          ao["ngay_tha"] = datetime.strptime(ao["ngay_tha"], "%Y-%m-%d").date()
        return data
    except Exception:
      pass
  return {
      "users": {
          "dangpham": {
              "password": "123",
              "ten": "Phạm Hải Đăng (Admin)",
              "role": "admin",
              "owner": "system",
          },
          "chuao_a": {
              "password": "123",
              "ten": "Anh Ba (Chủ Ao)",
              "role": "manager",
              "owner": "system",
          },
          "nhanvien_cuadang": {
              "password": "123",
              "ten": "Nhân viên của Đăng",
              "role": "staff",
              "owner": "dangpham",
          },
      },
      "data_ao": [
          {
              "id": "ao_1",
              "chu_so_huu": "dangpham",
              "ten": "Ao (Nuôi số 1)",
              "ngay_tha": datetime.today().date() - timedelta(days=2),
              "so_ngay": 120,
              "chu_ky_khoang": 4,      # Chu kỳ tạc vôi / khoáng: 4 ngày
              "chu_ky_vitamin": 5,     # Chu kỳ tạc Vitamin C: 5 ngày
              "ph_log": {},
          }
      ],
  }


def save_data():
  data_to_save = {
      "users": st.session_state.users,
      "data_ao": [],
  }
  for ao in st.session_state.data_ao:
    ao_copy = ao.copy()
    ao_copy["ngay_tha"] = ao["ngay_tha"].strftime("%Y-%m-%d")
    data_to_save["data_ao"].append(ao_copy)

  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)


if "initialized" not in st.session_state:
  saved_data = load_data()
  st.session_state.users = saved_data["users"]
  st.session_state.data_ao = saved_data["data_ao"]
  st.session_state.initialized = True

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.current_user = None

# --- GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center;'>🔐 Đăng Nhập Hệ Thống Quản Lý</h2>",
      unsafe_allow_html=True,
  )

  with st.form("login_form"):
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    submit_login = st.form_submit_button("Đăng Nhập")

    if submit_login:
      if (
          username in st.session_state.users
          and st.session_state.users[username]["password"] == password
      ):
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.rerun()
      else:
        st.error("Sai tài khoản hoặc mật khẩu!")
  st.stop()

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---
user_info = st.session_state.users[st.session_state.current_user]
st.sidebar.title(f"Chào, {user_info['ten']}")

# TÍNH NĂNG ĐỔI MẬT KHẨU CÁ NHÂN
with st.sidebar.expander("🔑 Đổi Mật Khẩu"):
  with st.form("change_password_form"):
    old_pass = st.text_input("Mật khẩu cũ", type="password")
    new_pass = st.text_input("Mật khẩu mới", type="password")
    confirm_pass = st.text_input("Xác nhận mật khẩu mới", type="password")
    submit_change_pass = st.form_submit_button("Cập Nhật Mật Khẩu")

    if submit_change_pass:
      if old_pass == user_info["password"]:
        if new_pass and new_pass == confirm_pass:
          user_info["password"] = new_pass
          save_data()
          st.success("Đổi mật khẩu thành công!")
        else:
          st.error("Mật khẩu mới không khớp hoặc bị để trống!")
      else:
        st.error("Mật khẩu cũ không chính xác!")

# TÍNH NĂNG TẠO TÀI KHOẢN MỚI
if user_info["role"] == "admin":
  with st.sidebar.expander("👤 Tạo Tài Khoản Mới"):
    with st.form("create_user_form_admin"):
      new_user_username = st.text_input("Tên đăng nhập mới")
      new_user_password = st.text_input("Mật khẩu", type="password")
      new_user_name = st.text_input("Tên hiển thị (Họ tên)")
      new_user_role = st.selectbox(
          "Vai trò",
          options=["manager", "staff"],
          format_func=lambda x: "Chủ ao (Manager)"
          if x == "manager"
          else "Nhân viên (Staff)",
      )
      submit_create_user = st.form_submit_button("Tạo Tài Khoản")

      if submit_create_user:
        if new_user_username and new_user_password and new_user_name:
          if new_user_username in st.session_state.users:
            st.error("Tên đăng nhập này đã tồn tại!")
          else:
            st.session_state.users[new_user_username] = {
                "password": new_user_password,
                "ten": new_user_name,
                "role": new_user_role,
                "owner": "dangpham"
                if new_user_role == "staff"
                else "system",
            }
            save_data()
            st.success(f"Đã tạo tài khoản '{new_user_name}' thành công!")
            st.rerun()
        else:
          st.error("Vui lòng điền đầy đủ thông tin!")

elif user_info["role"] == "manager":
  with st.sidebar.expander("👤 Tạo Tài Khoản Nhân Viên"):
    with st.form("create_user_form_manager"):
      new_user_username = st.text_input("Tên đăng nhập nhân viên")
      new_user_password = st.text_input("Mật khẩu", type="password")
      new_user_name = st.text_input("Tên hiển thị nhân viên")
      submit_create_staff = st.form_submit_button("Tạo Tài Khoản Nhân Viên")

      if submit_create_staff:
        if new_user_username and new_user_password and new_user_name:
          if new_user_username in st.session_state.users:
            st.error("Tên đăng nhập này đã tồn tại!")
          else:
            st.session_state.users[new_user_username] = {
                "password": new_user_password,
                "ten": new_user_name,
                "role": "staff",
                "owner": st.session_state.current_user,
            }
            save_data()
            st.success(f"Đã tạo tài khoản nhân viên '{new_user_name}' thành công!")
            st.rerun()
        else:
          st.error("Vui lòng điền đầy đủ thông tin!")

if st.sidebar.button("Đăng Xuất"):
  st.session_state.logged_in = False
  st.session_state.current_user = None
  st.rerun()

st.title("💧 Hệ Thống Quản Lý Ao Nuôi")

# --- SỔ TAY HƯỚNG DẪN & PHÁC ĐỒ TRỊ BỆNH CỐ ĐỊNH (ĐÃ CẬP NHẬT CHUẨN) ---
with st.expander("📖 Sổ Tay Hướng Dẫn & Phác Đồ Trị Bệnh (Cố Định)", expanded=True):
  st.markdown("""
### 1. Chuẩn Bị Trước Khi Thả:
- Tạc vôi số lượng: **4kg / 1 ao**
- Kết hợp: **50g thuốc tím**
- Thời điểm: Tiến hành trước khi thả giống **5 ngày**.

### 2. Tạc Vôi & Vitamin C Định Kỳ:
- **Tạc vôi định kỳ:** **1kg / 1 ao** (Chu kỳ: **4 ngày / lần**).
- **Tạc Vitamin C:** **20g / 1 ao** (Chu kỳ: **5 ngày / lần**).

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

# BẢNG QUẢN LÝ TÀI KHOẢN VÀ XEM AO CỦA NGƯỜI KHÁC (DÀNH CHO ADMIN)
if user_info["role"] == "admin":
  with st.expander("👥 Quản Lý Danh Sách Tài Khoản & Xem Ao Của Chủ Khác"):
    st.markdown("### Danh sách tài khoản trong hệ thống:")
    user_data_list = []
    for u_id, u_val in st.session_state.users.items():
      user_data_list.append({
          "Username": u_id,
          "Họ tên": u_val["ten"],
          "Vai trò": u_val["role"],
          "Quản lý bởi": u_val["owner"],
      })
    st.dataframe(
        pd.DataFrame(user_data_list), use_container_width=True, hide_index=True
    )

# Lọc danh sách ao theo quyền hạn
if user_info["role"] == "admin":
  danh_sach_chu_ao = list(
      set(
          [
              u_id
              for u_id, u_val in st.session_state.users.items()
              if u_val["role"] in ["admin", "manager"]
          ]
      )
  )

  mapping_chu_ao = {
      u_id: st.session_state.users[u_id]["ten"] for u_id in danh_sach_chu_ao
  }

  chon_chu_ao_xem = st.selectbox(
      "🔍 Lọc xem ao theo chủ sở hữu:",
      options=["all"] + danh_sach_chu_ao,
      format_func=lambda x: "Tất cả các ao"
      if x == "all"
      else f"Ao của: {mapping_chu_ao[x]}",
  )

  if chon_chu_ao_xem == "all":
    danh_sach_ao_hien_thi = st.session_state.data_ao
  else:
    danh_sach_ao_hien_thi = [
        ao for ao in st.session_state.data_ao if ao["chu_so_huu"] == chon_chu_ao_xem
    ]

elif user_info["role"] == "manager":
  danh_sach_ao_hien_thi = [
      ao
      for ao in st.session_state.data_ao
      if ao["chu_so_huu"] == st.session_state.current_user
  ]
else:
  quan_ly_truc_thuoc = user_info["owner"]
  danh_sach_ao_hien_thi = [
      ao for ao in st.session_state.data_ao if ao["chu_so_huu"] == quan_ly_truc_thuoc
  ]

# Thêm ao mới
if user_info["role"] in ["admin", "manager"]:
  with st.expander("➕ Thêm Ao Nuôi Mới"):
    with st.form("new_ao_form"):
      new_ten = st.text_input("Tên Ao Nuôi")
      new_ngay_tha = st.date_input(
          "Ngày Thả Giống", value=datetime.today().date()
      )
      new_so_ngay = st.number_input("Số ngày nuôi dự kiến", value=120, step=1)
      submit_new_ao = st.form_submit_button("Tạo Ao Mới")

      if submit_new_ao and new_ten:
        new_id = f"ao_{len(st.session_state.data_ao) + 1}"
        owner_id = (
            st.session_state.current_user
            if user_info["role"] == "manager"
            else "dangpham"
        )
        st.session_state.data_ao.append({
            "id": new_id,
            "chu_so_huu": owner_id,
            "ten": new_ten,
            "ngay_tha": new_ngay_tha,
            "so_ngay": int(new_so_ngay),
            "chu_ky_khoang": 4,   # Cập nhật chuẩn 4 ngày tạc vôi
            "chu_ky_vitamin": 5,  # Cập nhật chuẩn 5 ngày tạc Vitamin C
            "ph_log": {},
        })
        save_data()
        st.success(f"Đã thêm ao '{new_ten}' thành công!")
        st.rerun()

if not danh_sach_ao_hien_thi:
  st.warning("Hiện tại không có ao nào trong hệ thống của bạn.")
  st.stop()

# Chọn ao
ten_cac_ao = [
    f"{ao['ten']} (Chủ: {st.session_state.users.get(ao['chu_so_huu'], {}).get('ten', ao['chu_so_huu'])})"
    for ao in danh_sach_ao_hien_thi
]
selected_ao_display = st.selectbox(
    "Chọn ao muốn kiểm tra chi tiết:",
    options=ten_cac_ao,
    index=None,
    placeholder="-- Vui lòng chọn ao muốn xem --",
)

if selected_ao_display is not None:
  selected_index = ten_cac_ao.index(selected_ao_display)
  current_ao = danh_sach_ao_hien_thi[selected_index]

  st.markdown(f"### 📌 Đang xem: {current_ao['ten']}")

  col_ngay1, col_ngay2 = st.columns(2)
  with col_ngay1:
    st.info(
        f"📅 **Ngày Thả Giống:** {current_ao['ngay_tha'].strftime('%d/%m/%Y')}"
    )
  with col_ngay2:
    ngay_thu_hoach = current_ao["ngay_tha"] + timedelta(
        days=current_ao["so_ngay"]
    )
    st.success(
        f"🏁 **Ngày Thu Hoạch Dự Kiến:** {ngay_thu_hoach.strftime('%d/%m/%Y')}"
    )

  with st.expander("⚙️ Chỉnh sửa thông tin ngày thả giống"):
    with st.form(f"edit_form_{current_ao['id']}"):
      sua_ngay_tha = st.date_input(
          "Thay đổi Ngày Thả Giống mới", value=current_ao["ngay_tha"]
      )
      sua_so_ngay = st.number_input(
          "Số ngày nuôi", value=current_ao["so_ngay"], step=1
      )
      submit_sua = st.form_submit_button("Cập Nhật & Reset Vụ Nuôi")

      if submit_sua:
        if sua_ngay_tha != current_ao["ngay_tha"]:
          current_ao["ph_log"] = {}
          st.warning("Đã phát hiện đổi ngày thả! Lịch sử pH đã được reset.")

        current_ao["ngay_tha"] = sua_ngay_tha
        current_ao["so_ngay"] = int(sua_so_ngay)
        save_data()
        st.success("Đã cập nhật thông tin thành công!")
        st.rerun()

  # --- TỰ ĐỘNG TÍNH TOÁN NGÀY HÔM NAY THEO THỰC TẾ ---
  ngay_hom_nay = datetime.today().date()
  so_ngay_nuoi_hien_tai = (ngay_hom_nay - current_ao["ngay_tha"]).days

  if so_ngay_nuoi_hien_tai < 0:
    hien_thi_ngay = 0
  elif so_ngay_nuoi_hien_tai > current_ao["so_ngay"]:
    hien_thi_ngay = current_ao["so_ngay"]
  else:
    hien_thi_ngay = so_ngay_nuoi_hien_tai

  key_hom_nay = f"Ngày {hien_thi_ngay}"

  # --- NHẬT KÝ ĐO PH ĐỘC LẬP TỪNG BUỔI ---
  st.subheader(
      f"💧 Nhập pH Hôm Nay: {key_hom_nay} ({ngay_hom_nay.strftime('%d/%m/%Y')})"
  )

  old_data = current_ao["ph_log"].get(
      key_hom_nay, {"sang": 0.0, "trua": 0.0, "chieu": 0.0}
  )

  col_s, col_t, col_c = st.columns(3)
  with col_s:
    ph_sang = st.number_input(
        "pH Sáng",
        min_value=0.0,
        max_value=14.0,
        value=float(old_data.get("sang", 0.0)),
        step=0.1,
        key=f"input_sang_{current_ao['id']}",
    )
    if st.button("💾 Lưu Sáng", key=f"btn_sang_{current_ao['id']}"):
      if key_hom_nay not in current_ao["ph_log"]:
        current_ao["ph_log"][key_hom_nay] = {"sang": 0.0, "trua": 0.0, "chieu": 0.0}
      current_ao["ph_log"][key_hom_nay]["sang"] = ph_sang
      save_data()
      st.success(f"Đã lưu pH Sáng ({ph_sang}) thành công!")
      st.rerun()

  with col_t:
    ph_trua = st.number_input(
        "pH Trưa",
        min_value=0.0,
        max_value=14.0,
        value=float(old_data.get("trua", 0.0)),
        step=0.1,
        key=f"input_trua_{current_ao['id']}",
    )
    if st.button("💾 Lưu Trưa", key=f"btn_trua_{current_ao['id']}"):
      if key_hom_nay not in current_ao["ph_log"]:
        current_ao["ph_log"][key_hom_nay] = {"sang": 0.0, "trua": 0.0, "chieu": 0.0}
      current_ao["ph_log"][key_hom_nay]["trua"] = ph_trua
      save_data()
      st.success(f"Đã lưu pH Trưa ({ph_trua}) thành công!")
      st.rerun()

  with col_c:
    ph_chieu = st.number_input(
        "pH Chiều",
        min_value=0.0,
        max_value=14.0,
        value=float(old_data.get("chieu", 0.0)),
        step=0.1,
        key=f"input_chieu_{current_ao['id']}",
    )
    if st.button("💾 Lưu Chiều", key=f"btn_chieu_{current_ao['id']}"):
      if key_hom_nay not in current_ao["ph_log"]:
        current_ao["ph_log"][key_hom_nay] = {"sang": 0.0, "trua": 0.0, "chieu": 0.0}
      current_ao["ph_log"][key_hom_nay]["chieu"] = ph_chieu
      save_data()
      st.success(f"Đã lưu pH Chiều ({ph_chieu}) thành công!")
      st.rerun()

  # --- LỊCH TRÌNH TÁC THUỐC ĐỊNH KỲ (CHUẨN 4 NGÀY VÔI, 5 NGÀY VITAMIN C) ---
  st.subheader("📋 Lịch Trình Tạc Thuốc Định Kỳ")
  lich_trinh_data = []
  for i in range(0, current_ao["so_ngay"] + 1):
    ngay_cu_the = current_ao["ngay_tha"] + timedelta(days=i)
    thu_trong_tuan = ngay_cu_the.strftime("%A")

    # Kiểm tra lịch trình theo ngày (Vôi 4 ngày/lần, Vitamin C 5 ngày/lần)
    if i == 0:
      cong_viec = "Thả giống"
    else:
      viec_list = []
      if i % current_ao.get("chu_ky_khoang", 4) == 0:
        viec_list.append("Tạc vôi định kỳ (1kg)")
      if i % current_ao.get("chu_ky_vitamin", 5) == 0:
        viec_list.append("Bổ sung Vitamin C (20g)")
      
      cong_viec = " + ".join(viec_list) if viec_list else "Theo dõi bình thường"

    key_moc = f"Ngày {i}"
    ph_info = current_ao["ph_log"].get(key_moc, None)
    if ph_info:
      s_val = ph_info.get("sang", "Chưa đo")
      t_val = ph_info.get("trua", "Chưa đo")
      c_val = ph_info.get("chieu", "Chưa đo")
      ph_str = f"Sáng: {s_val} | Trưa: {t_val} | Chiều: {c_val}"
    else:
      ph_str = "Chưa đo"

    trang_thai_ngay = f"{ngay_cu_the.strftime('%d/%m/%Y')} ({thu_trong_tuan})"
    if i == hien_thi_ngay:
      trang_thai_ngay += " 👈 (Hôm nay)"

    lich_trinh_data.append({
        "Ngày": f"Ngày {i}",
        "Thứ ngày": trang_thai_ngay,
        "Công việc tạc thuốc": cong_viec,
        "pH (Sáng/Trưa/Chiều)": ph_str,
    })

  df_lich = pd.DataFrame(lich_trinh_data)
  st.dataframe(df_lich, use_container_width=True, hide_index=True)
