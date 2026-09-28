import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd

# =========================
# CẤU HÌNH
# =========================
st.set_page_config(
    page_title="Hotel Management",
    page_icon="🏨",
    layout="wide"
)

DB_NAME = "hotel_management.db"

st.image("VT.jpg")
# =========================
# DATABASE
# =========================
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Trống'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            phone TEXT,
            id_card TEXT,
            room_number TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT,
            adults INTEGER DEFAULT 1,
            children INTEGER DEFAULT 0,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Đang ở'
        )
    """)

    # Tạo dữ liệu phòng mẫu nếu database chưa có phòng
    cursor.execute("SELECT COUNT(*) FROM rooms")
    room_count = cursor.fetchone()[0]

    if room_count == 0:
        sample_rooms = [
            ("101", "Phòng đơn", 400000, "Trống"),
            ("102", "Phòng đơn", 400000, "Trống"),
            ("103", "Phòng đôi", 600000, "Trống"),
            ("104", "Phòng đôi", 600000, "Trống"),
            ("201", "Phòng đôi", 650000, "Trống"),
            ("202", "Phòng đôi", 650000, "Trống"),
            ("203", "Phòng gia đình", 900000, "Trống"),
            ("204", "Phòng gia đình", 900000, "Trống"),
            ("301", "Phòng VIP", 1200000, "Trống"),
            ("302", "Phòng VIP", 1200000, "Trống"),
        ]

        cursor.executemany("""
            INSERT INTO rooms
            (room_number, room_type, price, status)
            VALUES (?, ?, ?, ?)
        """, sample_rooms)

    conn.commit()
    conn.close()


init_database()


# =========================
# HÀM DATABASE
# =========================
def get_rooms():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM rooms ORDER BY room_number",
        conn
    )
    conn.close()
    return df


def get_guests():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM guests ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def update_room_status(room_number, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE rooms SET status = ? WHERE room_number = ?",
        (status, room_number)
    )

    conn.commit()
    conn.close()


# =========================
# SIDEBAR
# =========================
st.sidebar.title("🏨 HOTEL MANAGER")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU",
    [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "👤 Khách lưu trú",
        "📥 Nhận phòng",
        "📤 Trả phòng",
        "➕ Thêm phòng"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Hotel Management System")
st.sidebar.caption("Streamlit + SQLite")


# =========================
# TRANG TỔNG QUAN
# =========================
if menu == "📊 Tổng quan":

    st.title("🏨 Hệ thống quản lý khách sạn")

    rooms = get_rooms()
    guests = get_guests()

    total_rooms = len(rooms)
    empty_rooms = len(rooms[rooms["status"] == "Trống"])
    occupied_rooms = len(rooms[rooms["status"] == "Đang ở"])
    cleaning_rooms = len(rooms[rooms["status"] == "Đang dọn"])
    maintenance_rooms = len(rooms[rooms["status"] == "Bảo trì"])

    active_guests = len(
        guests[guests["status"] == "Đang ở"]
    ) if not guests.empty else 0

    revenue = (
        guests["total_amount"].sum()
        if not guests.empty
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏨 Tổng số phòng", total_rooms)
    col2.metric("🟢 Phòng trống", empty_rooms)
    col3.metric("🔴 Đang có khách", occupied_rooms)
    col4.metric("👥 Khách đang ở", active_guests)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric("🧹 Đang dọn", cleaning_rooms)
    col2.metric("🔧 Bảo trì", maintenance_rooms)
    col3.metric(
        "💰 Doanh thu",
        f"{revenue:,.0f} VNĐ"
    )

    st.subheader("📌 Tình trạng phòng")

    if not rooms.empty:
        display_rooms = rooms[
            ["room_number", "room_type", "price", "status"]
        ].copy()

        display_rooms.columns = [
            "Số phòng",
            "Loại phòng",
            "Giá/đêm",
            "Trạng thái"
        ]

        display_rooms["Giá/đêm"] = display_rooms[
            "Giá/đêm"
        ].apply(lambda x: f"{x:,.0f} VNĐ")

        st.dataframe(
            display_rooms,
            use_container_width=True,
            hide_index=True
        )


# =========================
# QUẢN LÝ PHÒNG
# =========================
elif menu == "🛏️ Quản lý phòng":

    st.title("🛏️ Quản lý phòng")

    rooms = get_rooms()

    search = st.text_input(
        "🔎 Tìm kiếm phòng",
        placeholder="Nhập số phòng..."
    )

    status_filter = st.selectbox(
        "Lọc theo trạng thái",
        [
            "Tất cả",
            "Trống",
            "Đang ở",
            "Đang dọn",
            "Bảo trì"
        ]
    )

    filtered = rooms.copy()

    if search:
        filtered = filtered[
            filtered["room_number"]
            .astype(str)
            .str.contains(search, case=False)
        ]

    if status_filter != "Tất cả":
        filtered = filtered[
            filtered["status"] == status_filter
        ]

    st.write(f"**Có {len(filtered)} phòng**")

    if not filtered.empty:

        for _, room in filtered.iterrows():

            status = room["status"]

            if status == "Trống":
                icon = "🟢"
            elif status == "Đang ở":
                icon = "🔴"
            elif status == "Đang dọn":
                icon = "🟡"
            else:
                icon = "🔧"

            with st.container(border=True):

                c1, c2, c3, c4, c5 = st.columns(
                    [1, 2, 2, 2, 2]
                )

                c1.markdown(
                    f"### {icon} {room['room_number']}"
                )

                c2.write(
                    f"**Loại:** {room['room_type']}"
                )

                c3.write(
                    f"**Giá:** {room['price']:,.0f} VNĐ"
                )

                c4.write(
                    f"**Trạng thái:** {status}"
                )

                new_status = c5.selectbox(
                    "Cập nhật",
                    [
                        "Trống",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ],
                    index=[
                        "Trống",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ].index(status),
                    key=f"status_{room['room_number']}"
                )

                if new_status != status:
                    update_room_status(
                        room["room_number"],
                        new_status
                    )
                    st.success(
                        f"Đã cập nhật phòng {room['room_number']}"
                    )
                    st.rerun()


# =========================
# KHÁCH LƯU TRÚ
# =========================
elif menu == "👤 Khách lưu trú":

    st.title("👤 Danh sách khách lưu trú")

    guests = get_guests()

    if guests.empty:
        st.info("Chưa có dữ liệu khách hàng.")
    else:

        search = st.text_input(
            "🔎 Tìm kiếm khách hàng",
            placeholder="Tên khách, số điện thoại hoặc số CCCD..."
        )

        filtered = guests.copy()

        if search:
            mask = (
                filtered["guest_name"]
                .astype(str)
                .str.contains(search, case=False)
                |
                filtered["phone"]
                .astype(str)
                .str.contains(search, case=False)
                |
                filtered["id_card"]
                .astype(str)
                .str.contains(search, case=False)
            )

            filtered = filtered[mask]

        display = filtered[
            [
                "guest_name",
                "phone",
                "id_card",
                "room_number",
                "check_in",
                "check_out",
                "adults",
                "children",
                "total_amount",
                "status"
            ]
        ].copy()

        display.columns = [
            "Họ tên",
            "Số điện thoại",
            "CCCD",
            "Phòng",
            "Nhận phòng",
            "Trả phòng",
            "Người lớn",
            "Trẻ em",
            "Tổng tiền",
            "Trạng thái"
        ]

        display["Tổng tiền"] = display[
            "Tổng tiền"
        ].apply(lambda x: f"{x:,.0f} VNĐ")

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )


# =========================
# NHẬN PHÒNG
# =========================
elif menu == "📥 Nhận phòng":

    st.title("📥 Nhận phòng")

    rooms = get_rooms()

    available_rooms = rooms[
        rooms["status"] == "Trống"
    ]

    if available_rooms.empty:

        st.warning(
            "⚠️ Hiện tại không còn phòng trống."
        )

    else:

        with st.form("checkin_form"):

            st.subheader("Thông tin khách hàng")

            col1, col2 = st.columns(2)

            with col1:
                guest_name = st.text_input(
                    "Họ và tên *"
                )

                phone = st.text_input(
                    "Số điện thoại"
                )

                id_card = st.text_input(
                    "CCCD / Hộ chiếu"
                )

            with col2:

                room_options = available_rooms[
                    "room_number"
                ].tolist()

                room_number = st.selectbox(
                    "Chọn phòng *",
                    room_options
                )

                check_in = st.date_input(
                    "Ngày nhận phòng",
                    value=date.today()
                )

                check_out = st.date_input(
                    "Ngày dự kiến trả phòng",
                    value=date.today()
                )

            col3, col4 = st.columns(2)

            with col3:
                adults = st.number_input(
                    "Số người lớn",
                    min_value=1,
                    value=1
                )

            with col4:
                children = st.number_input(
                    "Số trẻ em",
                    min_value=0,
                    value=0
                )

            submit = st.form_submit_button(
                "📥 Xác nhận nhận phòng",
                use_container_width=True
            )

            if submit:

                if not guest_name.strip():
                    st.error(
                        "Vui lòng nhập họ tên khách."
                    )

                elif check_out < check_in:
                    st.error(
                        "Ngày trả phòng không hợp lệ."
                    )

                else:

                    room_price = float(
                        available_rooms[
                            available_rooms["room_number"]
                            == room_number
                        ]["price"].iloc[0]
                    )

                    nights = (
                        check_out - check_in
                    ).days

                    if nights == 0:
                        nights = 1

                    total = room_price * nights

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO guests (
                            guest_name,
                            phone,
                            id_card,
                            room_number,
                            check_in,
                            check_out,
                            adults,
                            children,
                            total_amount,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        guest_name,
                        phone,
                        id_card,
                        room_number,
                        check_in.isoformat(),
                        check_out.isoformat(),
                        adults,
                        children,
                        total,
                        "Đang ở"
                    ))

                    cursor.execute("""
                        UPDATE rooms
                        SET status = 'Đang ở'
                        WHERE room_number = ?
                    """, (room_number,))

                    conn.commit()
                    conn.close()

                    st.success(
                        f"Đã nhận phòng {room_number} thành công!"
                    )

                    st.info(
                        f"💰 Tổng tiền dự kiến: "
                        f"{total:,.0f} VNĐ"
                    )

                    st.rerun()


# =========================
# TRẢ PHÒNG
# =========================
elif menu == "📤 Trả phòng":

    st.title("📤 Trả phòng")

    conn = get_connection()

    active_guests = pd.read_sql_query("""
        SELECT *
        FROM guests
        WHERE status = 'Đang ở'
        ORDER BY room_number
    """, conn)

    conn.close()

    if active_guests.empty:

        st.info("Hiện không có khách đang lưu trú.")

    else:

        room_list = active_guests[
            "room_number"
        ].tolist()

        selected_room = st.selectbox(
            "Chọn phòng trả",
            room_list
        )

        guest = active_guests[
            active_guests["room_number"]
            == selected_room
        ].iloc[0]

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Khách hàng:** {guest['guest_name']}"
            )

            st.write(
                f"**Số điện thoại:** {guest['phone']}"
            )

            st.write(
                f"**CCCD:** {guest['id_card']}"
            )

            st.write(
                f"**Phòng:** {guest['room_number']}"
            )

        with col2:

            st.write(
                f"**Ngày nhận:** {guest['check_in']}"
            )

            st.write(
                f"**Ngày dự kiến trả:** {guest['check_out']}"
            )

            st.write(
                f"**Số người lớn:** {guest['adults']}"
            )

            st.write(
                f"**Số trẻ em:** {guest['children']}"
            )

        st.markdown("---")

        actual_check_out = st.date_input(
            "Ngày trả phòng",
            value=date.today()
        )

        st.write(
            f"### 💰 Tổng tiền: "
            f"{guest['total_amount']:,.0f} VNĐ"
        )

        confirm = st.button(
            "📤 Xác nhận trả phòng",
            type="primary",
            use_container_width=True
        )

        if confirm:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE guests
                SET status = 'Đã trả',
                    check_out = ?
                WHERE id = ?
            """, (
                actual_check_out.isoformat(),
                int(guest["id"])
            ))

            cursor.execute("""
                UPDATE rooms
                SET status = 'Đang dọn'
                WHERE room_number = ?
            """, (selected_room,))

            conn.commit()
            conn.close()

            st.success(
                f"Đã trả phòng {selected_room} thành công."
            )

            st.info(
                "Phòng đã được chuyển sang trạng thái "
                "'Đang dọn'."
            )

            st.rerun()


# =========================
# THÊM PHÒNG
# =========================
elif menu == "➕ Thêm phòng":

    st.title("➕ Thêm phòng mới")

    with st.form("add_room_form"):

        col1, col2 = st.columns(2)

        with col1:

            room_number = st.text_input(
                "Số phòng *",
                placeholder="Ví dụ: 305"
            )

            room_type = st.selectbox(
                "Loại phòng",
                [
                    "Phòng đơn",
                    "Phòng đôi",
                    "Phòng gia đình",
                    "Phòng VIP"
                ]
            )

        with col2:

            price = st.number_input(
                "Giá phòng / đêm (VNĐ)",
                min_value=0,
                value=500000,
                step=50000
            )

            status = st.selectbox(
                "Trạng thái ban đầu",
                [
                    "Trống",
                    "Đang dọn",
                    "Bảo trì"
                ]
            )

        submit = st.form_submit_button(
            "➕ Thêm phòng",
            use_container_width=True
        )

        if submit:

            if not room_number.strip():

                st.error(
                    "Vui lòng nhập số phòng."
                )

            else:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    cursor.execute("""
                        INSERT INTO rooms (
                            room_number,
                            room_type,
                            price,
                            status
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        room_number.strip(),
                        room_type,
                        price,
                        status
                    ))

                    conn.commit()
                    st.success(
                        f"Đã thêm phòng {room_number}."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Số phòng này đã tồn tại."
                    )

                finally:
                    conn.close()

    st.markdown("---")

    st.subheader("📋 Danh sách phòng hiện có")

    rooms = get_rooms()

    display = rooms[
        [
            "room_number",
            "room_type",
            "price",
            "status"
        ]
    ].copy()

    display.columns = [
        "Số phòng",
        "Loại phòng",
        "Giá/đêm",
        "Trạng thái"
    ]

    display["Giá/đêm"] = display[
        "Giá/đêm"
    ].apply(lambda x: f"{x:,.0f} VNĐ")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )


# =========================
# FOOTER
# =========================
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Hotel Management System")
