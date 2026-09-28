import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date
import pandas as pd

# =========================================================
# CẤU HÌNH STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Hotel Management",
    page_icon="🏨",
    layout="wide"
)

DB_CONFIG = {
    "host": "mysql-29a6db25-tranthikimnguyet8-df0c.i.aivencloud.com",
    "port": 19586,
    "user": "avnadmin",
    "password": "AVNS_6y8qIYGcoOj22F0rJKB",
    "database": "defaultdb",
    "ssl_disabled": False
}

# =========================================================
# HÌNH ẢNH
# =========================================================

try:
    st.image("VT.jpg", use_container_width=True)
except:
    pass


# =========================================================
# KẾT NỐI MYSQL
# =========================================================

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"❌ Không thể kết nối MySQL: {e}")
        return None


# =========================================================
# KHỞI TẠO DATABASE
# =========================================================

def init_database():

    conn = get_connection()

    if conn is None:
        return

    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # BẢNG ROOMS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(20) NOT NULL UNIQUE,
                room_type VARCHAR(100) NOT NULL,
                price DECIMAL(15,2) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Trống'
            )
        """)

        # -------------------------------------------------
        # BẢNG GUESTS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guest_name VARCHAR(255) NOT NULL,
                phone VARCHAR(30),
                id_card VARCHAR(50),
                room_number VARCHAR(20) NOT NULL,
                check_in DATE NOT NULL,
                check_out DATE,
                adults INT DEFAULT 1,
                children INT DEFAULT 0,
                total_amount DECIMAL(15,2) DEFAULT 0,
                status VARCHAR(50) DEFAULT 'Đang ở'
            )
        """)

        # -------------------------------------------------
        # KIỂM TRA PHÒNG MẪU
        # -------------------------------------------------

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
                ("302", "Phòng VIP", 1200000, "Trống")
            ]

            cursor.executemany("""
                INSERT INTO rooms
                (
                    room_number,
                    room_type,
                    price,
                    status
                )
                VALUES (%s, %s, %s, %s)
            """, sample_rooms)

        conn.commit()

    except Error as e:

        st.error(
            f"❌ Lỗi khởi tạo cơ sở dữ liệu: {e}"
        )

    finally:

        cursor.close()
        conn.close()


# Chạy khởi tạo database
init_database()


# =========================================================
# HÀM LẤY DANH SÁCH PHÒNG
# =========================================================

def get_rooms():

    conn = get_connection()

    if conn is None:
        return pd.DataFrame()

    try:

        df = pd.read_sql(
            """
            SELECT
                id,
                room_number,
                room_type,
                price,
                status
            FROM rooms
            ORDER BY room_number
            """,
            conn
        )

        return df

    except Exception as e:

        st.error(f"❌ Lỗi lấy dữ liệu phòng: {e}")

        return pd.DataFrame()

    finally:

        conn.close()


# =========================================================
# HÀM LẤY KHÁCH
# =========================================================

def get_guests():

    conn = get_connection()

    if conn is None:
        return pd.DataFrame()

    try:

        df = pd.read_sql(
            """
            SELECT
                id,
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
            FROM guests
            ORDER BY id DESC
            """,
            conn
        )

        return df

    except Exception as e:

        st.error(f"❌ Lỗi lấy dữ liệu khách: {e}")

        return pd.DataFrame()

    finally:

        conn.close()


# =========================================================
# CẬP NHẬT TRẠNG THÁI PHÒNG
# =========================================================

def update_room_status(room_number, status):

    conn = get_connection()

    if conn is None:
        return False

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE rooms
            SET status = %s
            WHERE room_number = %s
            """,
            (
                status,
                room_number
            )
        )

        conn.commit()

        return True

    except Error as e:

        st.error(
            f"❌ Không thể cập nhật phòng: {e}"
        )

        return False

    finally:

        cursor.close()
        conn.close()


# =========================================================
# SIDEBAR
# =========================================================

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

st.sidebar.caption(
    "Hotel Management System"
)

st.sidebar.caption(
    "Streamlit + MySQL + Aiven"
)


# =========================================================
# TRANG TỔNG QUAN
# =========================================================

if menu == "📊 Tổng quan":

    st.title("🏨 HỆ THỐNG QUẢN LÝ KHÁCH SẠN")

    st.write(
        "Quản lý phòng, khách lưu trú, nhận phòng và trả phòng."
    )

    rooms = get_rooms()
    guests = get_guests()

    # -----------------------------------------------------
    # THỐNG KÊ PHÒNG
    # -----------------------------------------------------

    total_rooms = len(rooms)

    empty_rooms = len(
        rooms[rooms["status"] == "Trống"]
    ) if not rooms.empty else 0

    occupied_rooms = len(
        rooms[rooms["status"] == "Đang ở"]
    ) if not rooms.empty else 0

    cleaning_rooms = len(
        rooms[rooms["status"] == "Đang dọn"]
    ) if not rooms.empty else 0

    maintenance_rooms = len(
        rooms[rooms["status"] == "Bảo trì"]
    ) if not rooms.empty else 0

    # -----------------------------------------------------
    # THỐNG KÊ KHÁCH
    # -----------------------------------------------------

    active_guests = len(
        guests[guests["status"] == "Đang ở"]
    ) if not guests.empty else 0

    # -----------------------------------------------------
    # DOANH THU
    # -----------------------------------------------------

    revenue = (
        guests["total_amount"].sum()
        if not guests.empty
        else 0
    )

    # -----------------------------------------------------
    # METRIC
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🏨 Tổng số phòng",
        total_rooms
    )

    col2.metric(
        "🟢 Phòng trống",
        empty_rooms
    )

    col3.metric(
        "🔴 Đang có khách",
        occupied_rooms
    )

    col4.metric(
        "👥 Khách đang ở",
        active_guests
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🧹 Đang dọn",
        cleaning_rooms
    )

    col2.metric(
        "🔧 Bảo trì",
        maintenance_rooms
    )

    col3.metric(
        "💰 Doanh thu",
        f"{revenue:,.0f} VNĐ"
    )

    st.markdown("---")

    # -----------------------------------------------------
    # DANH SÁCH PHÒNG
    # -----------------------------------------------------

    st.subheader("📌 Tình trạng phòng")

    if rooms.empty:

        st.info(
            "Chưa có dữ liệu phòng."
        )

    else:

        display_rooms = rooms[
            [
                "room_number",
                "room_type",
                "price",
                "status"
            ]
        ].copy()

        display_rooms.columns = [
            "Số phòng",
            "Loại phòng",
            "Giá/đêm",
            "Trạng thái"
        ]

        display_rooms["Giá/đêm"] = (
            display_rooms["Giá/đêm"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

        st.dataframe(
            display_rooms,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# QUẢN LÝ PHÒNG
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.title("🛏️ Quản lý phòng")

    rooms = get_rooms()

    if rooms.empty:

        st.info(
            "Chưa có dữ liệu phòng."
        )

    else:

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

        # Tìm kiếm
        if search:

            filtered = filtered[
                filtered["room_number"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        # Lọc trạng thái
        if status_filter != "Tất cả":

            filtered = filtered[
                filtered["status"]
                == status_filter
            ]

        st.write(
            f"**Có {len(filtered)} phòng**"
        )

        # -------------------------------------------------
        # HIỂN THỊ PHÒNG
        # -------------------------------------------------

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
                    f"**Giá:** "
                    f"{room['price']:,.0f} VNĐ"
                )

                c4.write(
                    f"**Trạng thái:** {status}"
                )

                status_list = [
                    "Trống",
                    "Đang ở",
                    "Đang dọn",
                    "Bảo trì"
                ]

                current_index = status_list.index(
                    status
                )

                new_status = c5.selectbox(
                    "Cập nhật",
                    status_list,
                    index=current_index,
                    key=f"status_{room['room_number']}"
                )

                if new_status != status:

                    success = update_room_status(
                        room["room_number"],
                        new_status
                    )

                    if success:

                        st.success(
                            f"Đã cập nhật phòng "
                            f"{room['room_number']} "
                            f"→ {new_status}"
                        )

                        st.rerun()


# =========================================================
# KHÁCH LƯU TRÚ
# =========================================================

elif menu == "👤 Khách lưu trú":

    st.title("👤 Danh sách khách lưu trú")

    guests = get_guests()

    if guests.empty:

        st.info(
            "Chưa có dữ liệu khách hàng."
        )

    else:

        search = st.text_input(
            "🔎 Tìm kiếm khách hàng",
            placeholder=(
                "Tên khách, số điện thoại "
                "hoặc số CCCD..."
            )
        )

        filtered = guests.copy()

        if search:

            mask = (
                filtered["guest_name"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered["phone"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered["id_card"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
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

        display["Tổng tiền"] = (
            display["Tổng tiền"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# NHẬN PHÒNG
# =========================================================

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

            st.subheader(
                "Thông tin khách hàng"
            )

            col1, col2 = st.columns(2)

            # -------------------------------------------------
            # THÔNG TIN KHÁCH
            # -------------------------------------------------

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

            # -------------------------------------------------
            # THÔNG TIN PHÒNG
            # -------------------------------------------------

            with col2:

                room_options = (
                    available_rooms[
                        "room_number"
                    ].tolist()
                )

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

            # -------------------------------------------------
            # SỐ KHÁCH
            # -------------------------------------------------

            col3, col4 = st.columns(2)

            with col3:

                adults = st.number_input(
                    "Số người lớn",
                    min_value=1,
                    value=1,
                    step=1
                )

            with col4:

                children = st.number_input(
                    "Số trẻ em",
                    min_value=0,
                    value=0,
                    step=1
                )

            submit = st.form_submit_button(
                "📥 Xác nhận nhận phòng",
                use_container_width=True
            )

            # -------------------------------------------------
            # XỬ LÝ NHẬN PHÒNG
            # -------------------------------------------------

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

                    selected_room = (
                        available_rooms[
                            available_rooms[
                                "room_number"
                            ] == room_number
                        ]
                    )

                    room_price = float(
                        selected_room[
                            "price"
                        ].iloc[0]
                    )

                    nights = (
                        check_out - check_in
                    ).days

                    if nights == 0:
                        nights = 1

                    total = room_price * nights

                    conn = get_connection()

                    if conn is not None:

                        cursor = conn.cursor()

                        try:

                            # Thêm khách
                            cursor.execute(
                                """
                                INSERT INTO guests
                                (
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
                                VALUES
                                (
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s
                                )
                                """,
                                (
                                    guest_name.strip(),
                                    phone.strip(),
                                    id_card.strip(),
                                    room_number,
                                    check_in,
                                    check_out,
                                    adults,
                                    children,
                                    total,
                                    "Đang ở"
                                )
                            )

                            # Cập nhật phòng
                            cursor.execute(
                                """
                                UPDATE rooms
                                SET status = 'Đang ở'
                                WHERE room_number = %s
                                """,
                                (room_number,)
                            )

                            conn.commit()

                            st.success(
                                f"Đã nhận phòng "
                                f"{room_number} thành công!"
                            )

                            st.info(
                                f"💰 Tổng tiền dự kiến: "
                                f"{total:,.0f} VNĐ"
                            )

                        except Error as e:

                            conn.rollback()

                            st.error(
                                f"❌ Lỗi nhận phòng: {e}"
                            )

                        finally:

                            cursor.close()
                            conn.close()

                        st.rerun()


# =========================================================
# TRẢ PHÒNG
# =========================================================

elif menu == "📤 Trả phòng":

    st.title("📤 Trả phòng")

    conn = get_connection()

    if conn is None:

        st.error(
            "Không thể kết nối cơ sở dữ liệu."
        )

    else:

        try:

            active_guests = pd.read_sql(
                """
                SELECT *
                FROM guests
                WHERE status = 'Đang ở'
                ORDER BY room_number
                """,
                conn
            )

        except Exception as e:

            st.error(
                f"Lỗi lấy danh sách khách: {e}"
            )

            active_guests = pd.DataFrame()

        finally:

            conn.close()

        if active_guests.empty:

            st.info(
                "Hiện không có khách đang lưu trú."
            )

        else:

            room_list = (
                active_guests[
                    "room_number"
                ].tolist()
            )

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
                    f"**Khách hàng:** "
                    f"{guest['guest_name']}"
                )

                st.write(
                    f"**Số điện thoại:** "
                    f"{guest['phone']}"
                )

                st.write(
                    f"**CCCD:** "
                    f"{guest['id_card']}"
                )

                st.write(
                    f"**Phòng:** "
                    f"{guest['room_number']}"
                )

            with col2:

                st.write(
                    f"**Ngày nhận:** "
                    f"{guest['check_in']}"
                )

                st.write(
                    f"**Ngày dự kiến trả:** "
                    f"{guest['check_out']}"
                )

                st.write(
                    f"**Số người lớn:** "
                    f"{guest['adults']}"
                )

                st.write(
                    f"**Số trẻ em:** "
                    f"{guest['children']}"
                )

            st.markdown("---")

            actual_check_out = st.date_input(
                "Ngày trả phòng",
                value=date.today()
            )

            st.write(
                "### 💰 Tổng tiền: "
                f"{guest['total_amount']:,.0f} VNĐ"
            )

            confirm = st.button(
                "📤 Xác nhận trả phòng",
                type="primary",
                use_container_width=True
            )

            if confirm:

                if actual_check_out < pd.to_datetime(
                    guest["check_in"]
                ).date():

                    st.error(
                        "Ngày trả phòng không hợp lệ."
                    )

                else:

                    conn = get_connection()

                    if conn is not None:

                        cursor = conn.cursor()

                        try:

                            # Cập nhật khách
                            cursor.execute(
                                """
                                UPDATE guests
                                SET
                                    status = 'Đã trả',
                                    check_out = %s
                                WHERE id = %s
                                """,
                                (
                                    actual_check_out,
                                    int(guest["id"])
                                )
                            )

                            # Cập nhật phòng
                            cursor.execute(
                                """
                                UPDATE rooms
                                SET status = 'Đang dọn'
                                WHERE room_number = %s
                                """,
                                (selected_room,)
                            )

                            conn.commit()

                            st.success(
                                f"Đã trả phòng "
                                f"{selected_room} thành công."
                            )

                            st.info(
                                "Phòng đã được chuyển sang "
                                "trạng thái 'Đang dọn'."
                            )

                        except Error as e:

                            conn.rollback()

                            st.error(
                                f"❌ Lỗi trả phòng: {e}"
                            )

                        finally:

                            cursor.close()
                            conn.close()

                        st.rerun()


# =========================================================
# THÊM PHÒNG
# =========================================================

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

                if conn is not None:

                    cursor = conn.cursor()

                    try:

                        cursor.execute(
                            """
                            INSERT INTO rooms
                            (
                                room_number,
                                room_type,
                                price,
                                status
                            )
                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s
                            )
                            """,
                            (
                                room_number.strip(),
                                room_type,
                                price,
                                status
                            )
                        )

                        conn.commit()

                        st.success(
                            f"Đã thêm phòng "
                            f"{room_number}."
                        )

                    except Error as e:

                        if e.errno == 1062:

                            st.error(
                                "❌ Số phòng này đã tồn tại."
                            )

                        else:

                            st.error(
                                f"❌ Không thể thêm phòng: {e}"
                            )

                    finally:

                        cursor.close()
                        conn.close()

    st.markdown("---")

    st.subheader(
        "📋 Danh sách phòng hiện có"
    )

    rooms = get_rooms()

    if not rooms.empty:

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

        display["Giá/đêm"] = (
            display["Giá/đêm"]
            .apply(
                lambda x:
                f"{x:,.0f} VNĐ"
            )
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Chưa có dữ liệu phòng."
        )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "© 2026 Hotel Management System"
)

st.sidebar.caption(
    "Database: MySQL Aiven"
)
