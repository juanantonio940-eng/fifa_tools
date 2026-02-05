"""
Modulo Control BD - icloud_accounts
Busqueda, edicion, insercion y eliminacion de cuentas iCloud en Supabase.
"""
import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
import os

DATABASE_URL = os.getenv("DATABASE_URL", "")

TABLE = "icloud_accounts"
COLUMNS = ["id", "MAIL_MADRE", "ALIAS", "PASSWORD", "PAQUETE", "created_at"]
SEARCHABLE = ["ALIAS", "MAIL_MADRE", "PASSWORD", "PAQUETE", "id"]
EDITABLE = ["MAIL_MADRE", "ALIAS", "PASSWORD", "PAQUETE"]

TRANSLATIONS = {
    "es": {
        "title": "Control BD - icloud_accounts",
        "search": "Buscar",
        "field": "Campo",
        "value": "Valor a buscar",
        "exact": "Busqueda exacta",
        "btn_search": "Buscar",
        "btn_clear": "Limpiar",
        "limit": "Limite de filas",
        "total": "Total en BD",
        "shown": "filas mostradas",
        "results": "Resultados",
        "edit_title": "Editar fila",
        "edit_select": "Selecciona una fila de la tabla para editar",
        "btn_save": "Guardar cambios",
        "btn_delete": "Eliminar fila",
        "btn_insert": "Insertar fila",
        "insert_title": "Insertar nueva fila",
        "btn_do_insert": "Insertar",
        "no_changes": "No hay cambios para guardar",
        "saved": "Fila actualizada correctamente",
        "deleted": "Fila eliminada correctamente",
        "inserted": "Fila insertada correctamente",
        "confirm_delete": "Estas seguro de eliminar esta fila?",
        "no_connection": "No se pudo conectar a la base de datos. Configura DATABASE_URL en las variables de entorno.",
        "fill_one": "Rellena al menos un campo",
        "connected": "Conectado a Supabase",
        "bulk_title": "Edicion masiva",
        "bulk_where_field": "Campo a buscar (WHERE)",
        "bulk_where_value": "Valor a buscar",
        "bulk_set_field": "Campo a modificar",
        "bulk_set_value": "Nuevo valor",
        "bulk_preview": "Vista previa",
        "bulk_affected": "filas afectadas",
        "bulk_execute": "Ejecutar actualizacion masiva",
        "bulk_confirm": "Estas seguro? Se actualizaran {n} filas.",
        "bulk_done": "{n} filas actualizadas correctamente",
        "bulk_fill": "Rellena todos los campos",
        "bulk_no_rows": "No se encontraron filas con ese criterio",
    },
    "en": {
        "title": "DB Control - icloud_accounts",
        "search": "Search",
        "field": "Field",
        "value": "Search value",
        "exact": "Exact match",
        "btn_search": "Search",
        "btn_clear": "Clear",
        "limit": "Row limit",
        "total": "Total in DB",
        "shown": "rows shown",
        "results": "Results",
        "edit_title": "Edit row",
        "edit_select": "Select a row from the table to edit",
        "btn_save": "Save changes",
        "btn_delete": "Delete row",
        "btn_insert": "Insert row",
        "insert_title": "Insert new row",
        "btn_do_insert": "Insert",
        "no_changes": "No changes to save",
        "saved": "Row updated successfully",
        "deleted": "Row deleted successfully",
        "inserted": "Row inserted successfully",
        "confirm_delete": "Are you sure you want to delete this row?",
        "no_connection": "Could not connect to database. Set DATABASE_URL in environment variables.",
        "fill_one": "Fill at least one field",
        "connected": "Connected to Supabase",
        "bulk_title": "Bulk edit",
        "bulk_where_field": "Match field (WHERE)",
        "bulk_where_value": "Value to match",
        "bulk_set_field": "Field to update",
        "bulk_set_value": "New value",
        "bulk_preview": "Preview",
        "bulk_affected": "rows affected",
        "bulk_execute": "Execute bulk update",
        "bulk_confirm": "Are you sure? {n} rows will be updated.",
        "bulk_done": "{n} rows updated successfully",
        "bulk_fill": "Fill all fields",
        "bulk_no_rows": "No rows found matching that criteria",
    },
    "hi": {
        "title": "DB Control - icloud_accounts",
        "search": "खोजें",
        "field": "फ़ील्ड",
        "value": "खोज मान",
        "exact": "सटीक मिलान",
        "btn_search": "खोजें",
        "btn_clear": "साफ करें",
        "limit": "पंक्ति सीमा",
        "total": "DB में कुल",
        "shown": "पंक्तियाँ दिखाई गईं",
        "results": "परिणाम",
        "edit_title": "पंक्ति संपादित करें",
        "edit_select": "संपादित करने के लिए तालिका से एक पंक्ति चुनें",
        "btn_save": "परिवर्तन सहेजें",
        "btn_delete": "पंक्ति हटाएं",
        "btn_insert": "पंक्ति डालें",
        "insert_title": "नई पंक्ति डालें",
        "btn_do_insert": "डालें",
        "no_changes": "सहेजने के लिए कोई परिवर्तन नहीं",
        "saved": "पंक्ति सफलतापूर्वक अपडेट की गई",
        "deleted": "पंक्ति सफलतापूर्वक हटाई गई",
        "inserted": "पंक्ति सफलतापूर्वक डाली गई",
        "confirm_delete": "क्या आप इस पंक्ति को हटाना चाहते हैं?",
        "no_connection": "डेटाबेस से कनेक्ट नहीं हो सका। DATABASE_URL सेट करें।",
        "fill_one": "कम से कम एक फ़ील्ड भरें",
        "connected": "Supabase से जुड़ा",
        "bulk_title": "सामूहिक संपादन",
        "bulk_where_field": "खोज फ़ील्ड (WHERE)",
        "bulk_where_value": "खोज मान",
        "bulk_set_field": "अपडेट फ़ील्ड",
        "bulk_set_value": "नया मान",
        "bulk_preview": "पूर्वावलोकन",
        "bulk_affected": "प्रभावित पंक्तियाँ",
        "bulk_execute": "सामूहिक अपडेट",
        "bulk_confirm": "क्या आप सुनिश्चित हैं? {n} पंक्तियाँ अपडेट होंगी।",
        "bulk_done": "{n} पंक्तियाँ सफलतापूर्वक अपडेट की गईं",
        "bulk_fill": "सभी फ़ील्ड भरें",
        "bulk_no_rows": "इस मापदंड से कोई पंक्ति नहीं मिली",
    },
}


def t(key):
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)


def get_connection():
    """Obtiene o reutiliza la conexion a la BD."""
    if "controlbd_conn" not in st.session_state or st.session_state.controlbd_conn is None or st.session_state.controlbd_conn.closed:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            st.session_state.controlbd_conn = conn
        except Exception as e:
            st.session_state.controlbd_conn = None
            raise e
    return st.session_state.controlbd_conn


def get_total_count(conn):
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(TABLE)))
    total = cur.fetchone()[0]
    cur.close()
    return total


def search_rows(conn, column, value, exact, limit, sort_col="id", sort_asc=True):
    direction = "ASC" if sort_asc else "DESC"
    cur = conn.cursor()

    if value:
        if exact:
            query = sql.SQL(
                "SELECT * FROM {} WHERE {} = %s ORDER BY {} " + direction + " LIMIT %s"
            ).format(sql.Identifier(TABLE), sql.Identifier(column), sql.Identifier(sort_col))
            cur.execute(query, (value, limit))
        else:
            if column == "id":
                query = sql.SQL(
                    "SELECT * FROM {} WHERE {}::text LIKE %s ORDER BY {} " + direction + " LIMIT %s"
                ).format(sql.Identifier(TABLE), sql.Identifier(column), sql.Identifier(sort_col))
            else:
                query = sql.SQL(
                    "SELECT * FROM {} WHERE {} ILIKE %s ORDER BY {} " + direction + " LIMIT %s"
                ).format(sql.Identifier(TABLE), sql.Identifier(column), sql.Identifier(sort_col))
            cur.execute(query, (f"%{value}%", limit))
    else:
        query = sql.SQL(
            "SELECT * FROM {} ORDER BY {} " + direction + " LIMIT %s"
        ).format(sql.Identifier(TABLE), sql.Identifier(sort_col))
        cur.execute(query, (limit,))

    rows = cur.fetchall()
    cur.close()
    return rows


def update_row(conn, row_id, changes):
    set_parts = []
    set_values = []
    for col, val in changes.items():
        set_parts.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
        set_values.append(val if val != "" else None)

    cur = conn.cursor()
    query = sql.SQL("UPDATE {} SET {} WHERE id = %s").format(
        sql.Identifier(TABLE),
        sql.SQL(", ").join(set_parts),
    )
    set_values.append(row_id)
    cur.execute(query, set_values)
    cur.close()


def insert_row(conn, data):
    cols = []
    vals = []
    for col, val in data.items():
        if val.strip():
            cols.append(col)
            vals.append(val.strip())

    cur = conn.cursor()
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(TABLE),
        sql.SQL(", ").join(map(sql.Identifier, cols)),
        sql.SQL(", ").join(sql.Placeholder() * len(vals)),
    )
    cur.execute(query, vals)
    cur.close()


def delete_row(conn, row_id):
    cur = conn.cursor()
    cur.execute(sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(TABLE)), (row_id,))
    cur.close()


def bulk_count(conn, where_col, where_val):
    """Cuenta cuantas filas coinciden con el criterio."""
    cur = conn.cursor()
    query = sql.SQL("SELECT count(*) FROM {} WHERE {} = %s").format(
        sql.Identifier(TABLE), sql.Identifier(where_col)
    )
    cur.execute(query, (where_val,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def bulk_update(conn, where_col, where_val, set_col, set_val):
    """Actualiza set_col = set_val en todas las filas donde where_col = where_val."""
    cur = conn.cursor()
    query = sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s").format(
        sql.Identifier(TABLE), sql.Identifier(set_col), sql.Identifier(where_col)
    )
    cur.execute(query, (set_val, where_val))
    affected = cur.rowcount
    cur.close()
    return affected


def render():
    st.title(f"🗄️ {t('title')}")

    if not DATABASE_URL:
        st.error(t("no_connection"))
        return

    try:
        conn = get_connection()
    except Exception as e:
        st.error(f"{t('no_connection')}\n\n`{e}`")
        return

    # Total en BD
    try:
        total = get_total_count(conn)
        st.caption(f"✅ {t('connected')} | {t('total')}: **{total:,}**")
    except Exception:
        st.caption(f"✅ {t('connected')}")

    # ── Busqueda ──────────────────────────────────────────────────────
    with st.container():
        col_field, col_value, col_exact, col_limit = st.columns([1, 2.5, 0.7, 0.8])

        with col_field:
            search_col = st.selectbox(t("field"), SEARCHABLE, key="cbd_search_col")
        with col_value:
            search_val = st.text_input(t("value"), key="cbd_search_val")
        with col_exact:
            exact = st.checkbox(t("exact"), key="cbd_exact")
        with col_limit:
            limit = st.number_input(t("limit"), min_value=10, max_value=10000, value=500, step=100, key="cbd_limit")

    col_btn1, col_btn2, _ = st.columns([1, 1, 6])
    with col_btn1:
        do_search = st.button(f"🔍 {t('btn_search')}", type="primary", use_container_width=True)
    with col_btn2:
        do_clear = st.button(f"🧹 {t('btn_clear')}", use_container_width=True)

    if do_clear:
        st.session_state.cbd_search_val = ""
        st.rerun()

    # Ejecutar busqueda (siempre al cargar o al pulsar buscar)
    try:
        rows = search_rows(conn, search_col, search_val, exact, limit)
    except Exception as e:
        st.error(str(e))
        return

    st.markdown(f"**{t('results')}:** {len(rows)} {t('shown')}")

    if not rows:
        st.info(t("btn_clear"))
        return

    # ── Tabla de resultados ───────────────────────────────────────────
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["created_at"] = df["created_at"].astype(str)

    # Mostrar con seleccion
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="cbd_table",
    )

    selected_rows = event.selection.rows if event.selection else []

    st.markdown("---")

    # ── Acciones: Editar / Masiva / Insertar ─────────────────────────
    tab_edit, tab_bulk, tab_insert = st.tabs([f"✏️ {t('edit_title')}", f"🔄 {t('bulk_title')}", f"➕ {t('insert_title')}"])

    # ── Tab Editar ──
    with tab_edit:
        if selected_rows:
            idx = selected_rows[0]
            row = df.iloc[idx]
            row_id = row["id"]

            st.caption(f"**ID:** {row_id} | **created_at:** {row['created_at']}")

            edit_cols = st.columns(len(EDITABLE))
            new_values = {}
            for i, col in enumerate(EDITABLE):
                with edit_cols[i]:
                    new_values[col] = st.text_input(
                        col, value=str(row[col]) if row[col] else "", key=f"cbd_edit_{col}"
                    )

            col_save, col_del, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button(f"💾 {t('btn_save')}", type="primary", use_container_width=True):
                    changes = {}
                    for col in EDITABLE:
                        old_val = str(row[col]) if row[col] else ""
                        if new_values[col] != old_val:
                            changes[col] = new_values[col]
                    if changes:
                        try:
                            update_row(conn, row_id, changes)
                            st.success(t("saved"))
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    else:
                        st.warning(t("no_changes"))

            with col_del:
                if st.button(f"🗑️ {t('btn_delete')}", use_container_width=True):
                    st.session_state.cbd_confirm_delete = row_id

            # Confirmacion de eliminacion
            if st.session_state.get("cbd_confirm_delete") == row_id:
                st.warning(t("confirm_delete"))
                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    if st.button("✅ Si, eliminar", type="primary"):
                        try:
                            delete_row(conn, row_id)
                            st.session_state.cbd_confirm_delete = None
                            st.success(t("deleted"))
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c2:
                    if st.button("❌ Cancelar"):
                        st.session_state.cbd_confirm_delete = None
                        st.rerun()
        else:
            st.info(t("edit_select"))

    # ── Tab Edicion Masiva ──
    with tab_bulk:
        st.caption("Actualiza un campo en todas las filas que coincidan con un criterio. "
                   "Ej: cambiar PASSWORD de todas las filas con un mismo MAIL_MADRE.")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            bulk_where_col = st.selectbox(t("bulk_where_field"), SEARCHABLE, key="cbd_bulk_wcol")
        with col_w2:
            bulk_where_val = st.text_input(t("bulk_where_value"), key="cbd_bulk_wval")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            bulk_set_col = st.selectbox(t("bulk_set_field"), EDITABLE, key="cbd_bulk_scol")
        with col_s2:
            bulk_set_val = st.text_input(t("bulk_set_value"), key="cbd_bulk_sval")

        col_prev, col_exec, _ = st.columns([1, 1.5, 3.5])

        with col_prev:
            do_preview = st.button(f"🔍 {t('bulk_preview')}", use_container_width=True)

        # Preview: contar filas afectadas
        if do_preview and bulk_where_val:
            try:
                count = bulk_count(conn, bulk_where_col, bulk_where_val)
                if count > 0:
                    st.session_state.cbd_bulk_count = count
                    st.info(f"**{count}** {t('bulk_affected')} ({bulk_where_col} = `{bulk_where_val}`)")
                else:
                    st.session_state.cbd_bulk_count = 0
                    st.warning(t("bulk_no_rows"))
            except Exception as e:
                st.error(str(e))
        elif do_preview:
            st.warning(t("bulk_fill"))

        with col_exec:
            if st.button(f"⚡ {t('bulk_execute')}", type="primary", use_container_width=True):
                if bulk_where_val and bulk_set_val:
                    st.session_state.cbd_bulk_pending = True
                else:
                    st.warning(t("bulk_fill"))

        # Confirmacion
        if st.session_state.get("cbd_bulk_pending"):
            try:
                count = bulk_count(conn, bulk_where_col, bulk_where_val)
            except Exception:
                count = 0

            if count == 0:
                st.warning(t("bulk_no_rows"))
                st.session_state.cbd_bulk_pending = False
            else:
                st.warning(t("bulk_confirm").format(n=count))
                st.caption(f"`UPDATE {TABLE} SET {bulk_set_col} = '{bulk_set_val}' WHERE {bulk_where_col} = '{bulk_where_val}'`")

                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    if st.button("✅ Confirmar", type="primary", key="cbd_bulk_yes"):
                        try:
                            affected = bulk_update(conn, bulk_where_col, bulk_where_val, bulk_set_col, bulk_set_val)
                            st.session_state.cbd_bulk_pending = False
                            st.success(t("bulk_done").format(n=affected))
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c2:
                    if st.button("❌ Cancelar", key="cbd_bulk_no"):
                        st.session_state.cbd_bulk_pending = False
                        st.rerun()

    # ── Tab Insertar ──
    with tab_insert:
        insert_values = {}
        ins_cols = st.columns(len(EDITABLE))
        for i, col in enumerate(EDITABLE):
            with ins_cols[i]:
                insert_values[col] = st.text_input(col, key=f"cbd_ins_{col}")

        if st.button(f"➕ {t('btn_do_insert')}", type="primary"):
            if any(v.strip() for v in insert_values.values()):
                try:
                    insert_row(conn, insert_values)
                    st.success(t("inserted"))
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning(t("fill_one"))
