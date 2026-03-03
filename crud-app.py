import streamlit as st
import gspread
import pandas as pd

# 設定頁面資訊
st.set_page_config(page_title="GSheet 控制台", layout="wide")

# ==========================================
# 1. 建立 Google Sheets 連線
# ==========================================
@st.cache_resource
def init_connection():
    try:
        credentials = dict(st.secrets["gcp_service_account"])
        gc = gspread.service_account_from_dict(credentials)
        return gc
    except Exception as e:
        st.error(f"❌ 認證失敗，請檢查 .streamlit/secrets.toml 設定。錯誤：{e}")
        st.stop()

gc = init_connection()

# ==========================================
# 2. 開啟指定的試算表與工作表
# ==========================================
SHEET_INPUT = "https://docs.google.com/spreadsheets/d/1Y2_ihmnsoOcioF0pPBuGc3F5ZIgJ_8TP1QSHCac18sA/edit?pli=1&gid=0#gid=0"
WORKSHEET_NAME = "sheet bot"

try:
    if SHEET_INPUT.startswith("http"):
        sh = gc.open_by_url(SHEET_INPUT)
    else:
        sh = gc.open(SHEET_INPUT)
    worksheet = sh.worksheet(WORKSHEET_NAME)
except Exception as e:
    st.error(f"無法開啟試算表，請確認權限或 URL。錯誤：{e}")
    st.stop()

st.title("📊 Google Sheets 讀寫測試儀表板")

# ==========================================
# 3. 讀取資料 (Read) - 增加快取處理
# ==========================================
st.header("1️⃣ 目前資料列表")

# 獲取所有資料
data = worksheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    # 建立顯示用的 DataFrame
    display_df = df.copy()
    display_df.insert(0, "試算表列數", range(2, len(data) + 2))
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("目前工作表中沒有資料。請確保第一列為標題（姓名, 數量）")

st.divider()

# ==========================================
# 4. 新增資料 (Create)
# ==========================================
st.header("2️⃣ 新增資料")

with st.form("add_data_form", clear_on_submit=True):
    col_name = st.text_input("姓名")
    col_qty = st.number_input("數量", min_value=0, step=1)
    submitted = st.form_submit_button("➕ 寫入 Google Sheet")

    if submitted:
        if not col_name.strip():
            st.warning("姓名不能為空")
        else:
            with st.spinner("寫入中..."):
                worksheet.append_row([col_name, col_qty])
                st.success("寫入成功！")
                st.rerun()

# ==========================================
# 5 & 6. 修改與刪除 (只有有資料才顯示)
# ==========================================
if data:
    st.divider()
    col_update, col_delete = st.columns(2)

    # 建立選項清單
    # 預防 Key 錯誤，改用索引安全存取
    row_options = {f"第 {i + 2} 列: {row.get('姓名', '未知')}": i + 2 for i, row in enumerate(data)}

    # --- 修改區塊 ---
    with col_update:
        st.header("3️⃣ 修改資料")
        selected_option_update = st.selectbox("選擇修改對象", options=list(row_options.keys()))
        row_idx = row_options[selected_option_update]
        
        # 取得該列原始資料
        current_val = data[row_idx - 2]
        
        with st.form("update_form"):
            upd_name = st.text_input("新姓名", value=current_val.get("姓名", ""))
            upd_qty = st.number_input("新數量", value=int(current_val.get("數量", 0)))
            if st.form_submit_button("💾 更新"):
                # 使用一次性更新整列，減少 API 呼叫
                worksheet.update(range_name=f"A{row_idx}:B{row_idx}", values=[[upd_name, upd_qty]])
                st.success("更新成功！")
                st.rerun()

    # --- 刪除區塊 ---
    with col_delete:
        st.header("4️⃣ 刪除資料")
        selected_option_del = st.selectbox("選擇刪除對象", options=list(row_options.keys()))
        del_idx = row_options[selected_option_del]
        
        st.warning(f"確定要刪除 {selected_option_del} 嗎？")
        if st.button("🗑️ 確認刪除", type="primary"):
            worksheet.delete_rows(del_idx)
            st.success("刪除成功！")
            st.rerun()
