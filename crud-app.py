import streamlit as st
import gspread
import pandas as pd


# ==========================================
# 1. 建立 Google Sheets 連線
# ==========================================
@st.cache_resource
def init_connection():
    credentials = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(credentials)
    return gc


gc = init_connection()

# ==========================================
# 2. 開啟指定的試算表與工作表
# ==========================================
SHEET_INPUT = "試算表網址"
WORKSHEET_NAME = "工作表1"

try:
    if SHEET_INPUT.startswith("http://") or SHEET_INPUT.startswith("https://"):
        sh = gc.open_by_url(SHEET_INPUT)
    else:
        sh = gc.open(SHEET_INPUT)
    worksheet = sh.worksheet(WORKSHEET_NAME)
except Exception as e:
    st.error(
        f"無法開啟試算表，請確認名稱/網址是否正確，且服務帳號 ({gc.auth.signer_email}) 已被加入共用編輯者！\n錯誤訊息：{e}")
    st.stop()

st.title("📊 Google Sheets 讀寫測試儀表板")
