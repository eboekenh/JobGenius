import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Manual Prompt ↔ Answer Logger", layout="wide")
st.title("📝 Manual Prompt ↔ Answer Logger")
st.caption("API yok. Requirement + ChatGPT cevabını elle gir → tabloya ekle → CSV indir.")

# ---------------- Session state ----------------
if "mpl_rows" not in st.session_state:
    st.session_state["mpl_rows"] = pd.DataFrame(columns=["ID", "Timestamp", "Requirement", "Answer"])
if "mpl_autoinc" not in st.session_state:
    st.session_state["mpl_autoinc"] = 1
if "mpl_clear_next" not in st.session_state:   # inputları güvenli temizleme bayrağı
    st.session_state["mpl_clear_next"] = False

# >>> Widgetlar oluşturulmadan ÖNCE temizliği yap
if st.session_state["mpl_clear_next"]:
    st.session_state["mpl_input_req"] = ""
    st.session_state["mpl_input_ans"] = ""
    st.session_state["mpl_clear_next"] = False

# ---------------- Inputs ----------------
c1, c2 = st.columns(2)
with c1:
    req = st.text_area("Requirement", height=180, key="mpl_input_req",
                       placeholder="İlana ait tek bir gereklilik / metin…")
with c2:
    ans = st.text_area("ChatGPT Answer (manuel yapıştır)", height=180, key="mpl_input_ans",
                       placeholder="ChatGPT’de üretilen cevabı buraya yapıştır…")

col_add, col_clear = st.columns(2)
with col_add:
    if st.button("➕ Add to table", use_container_width=True, key="mpl_add"):
        if not req.strip() or not ans.strip():
            st.warning("İki alan da boş olamaz.")
        else:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rid = st.session_state["mpl_autoinc"]; st.session_state["mpl_autoinc"] += 1
            new_row = pd.DataFrame([{"ID": rid, "Timestamp": ts,
                                     "Requirement": req.strip(), "Answer": ans.strip()}])
            st.session_state["mpl_rows"] = pd.concat([st.session_state["mpl_rows"], new_row], ignore_index=True)
            st.success("Satır eklendi.")
            # inputları bu run'da DEĞİL, bir sonrakinde temizle
            st.session_state["mpl_clear_next"] = True
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

with col_clear:
    if st.button("🧹 Clear inputs", use_container_width=True, key="mpl_clear"):
        st.session_state["mpl_clear_next"] = True
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()

st.markdown("---")

# ---------------- Table (editable) + delete ----------------
st.subheader("📒 Kayıt Tablosu (düzenlenebilir)")
table = st.session_state["mpl_rows"].copy()
if not table.empty and "Delete" not in table.columns:
    table.insert(0, "Delete", False)

edited = st.data_editor(
    table,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "Delete": st.column_config.CheckboxColumn("Delete", help="Silmek istediklerini işaretle"),
        "Requirement": st.column_config.TextColumn(width="medium"),
        "Answer": st.column_config.TextColumn(width="medium"),
    },
    height=360,
    key="mpl_editor",
)

cA, cB, _ = st.columns([1, 1, 2])
with cA:
    if st.button("💾 Apply edits", use_container_width=True, key="mpl_apply"):
        st.session_state["mpl_rows"] = edited.drop(columns=["Delete"], errors="ignore")
        st.success("Düzenlemeler uygulandı.")
with cB:
    if st.button("🗑️ Delete selected", use_container_width=True, key="mpl_delete"):
        delete_mask = edited["Delete"] if "Delete" in edited.columns else pd.Series([False]*len(edited))
        keep = edited.loc[~delete_mask].drop(columns=["Delete"], errors="ignore").reset_index(drop=True)
        st.session_state["mpl_rows"] = keep
        st.success("Seçili satırlar silindi.")

st.markdown("---")

# ---------------- CSV import / export ----------------
st.subheader("⬇️⬆️ CSV")
col_imp, col_exp = st.columns(2)

with col_imp:
    up = st.file_uploader("CSV içe aktar (opsiyonel)", type=["csv"], key="mpl_upload")
    mode = st.radio("İçe aktarırken:", ["Append", "Replace"], horizontal=True, key="mpl_mode")
    if up is not None:
        try:
            df_in = pd.read_csv(up)
            cols_lower = [c.lower() for c in df_in.columns]
            if {"requirement", "answer"}.issubset(set(cols_lower)):
                req_col = df_in.columns[cols_lower.index("requirement")]
                ans_col = df_in.columns[cols_lower.index("answer")]
                use = df_in[[req_col, ans_col]].rename(columns={req_col: "Requirement", ans_col: "Answer"})
            else:
                use = df_in.select_dtypes(include="object").iloc[:, :2].copy()
                use.columns = ["Requirement", "Answer"]

            use = use.dropna(how="all")
            use["Requirement"] = use["Requirement"].astype(str).str.strip()
            use["Answer"]      = use["Answer"].astype(str).str.strip()
            use = use[(use["Requirement"] != "") | (use["Answer"] != "")]

            if st.button("📥 Import now", key="mpl_import_now"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_id = st.session_state["mpl_autoinc"]
                ids = list(range(start_id, start_id + len(use)))
                st.session_state["mpl_autoinc"] += len(use)
                use_full = pd.DataFrame({
                    "ID": ids,
                    "Timestamp": now,
                    "Requirement": use["Requirement"].values,
                    "Answer": use["Answer"].values,
                })
                if mode == "Replace":
                    st.session_state["mpl_rows"] = use_full
                else:
                    st.session_state["mpl_rows"] = pd.concat([st.session_state["mpl_rows"], use_full], ignore_index=True)
                st.success(f"{len(use)} satır içe aktarıldı.")
        except Exception as e:
            st.error(f"CSV okunamadı: {e}")

with col_exp:
    csv_bytes = st.session_state["mpl_rows"].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        data=csv_bytes,
        file_name="manual_prompt_logs.csv",
        mime="text/csv",
        use_container_width=True,
        key="mpl_download",
    )

# ---------------- Danger zone ----------------
with st.expander("🛑 Danger zone"):
    if st.button("Tüm tabloyu temizle (geri alınamaz)", type="primary", key="mpl_wipe"):
        st.session_state["mpl_rows"] = st.session_state["mpl_rows"].iloc[0:0]
        st.session_state["mpl_autoinc"] = 1
        st.success("Tablo temizlendi.")
