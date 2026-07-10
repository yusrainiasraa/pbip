import streamlit as st
import zipfile
import io
import os

st.set_page_config(page_title="PBIX to PBIP Converter", layout="centered")

st.title("📊 PBIX to PBIP Converter")
st.write("Upload file `.pbix` Anda, dan aplikasi akan mengonversinya menjadi struktur folder `.pbip` dalam bentuk file ZIP.")

# 1. File Uploader
uploaded_file = st.file_uploader("Pilih file Power BI (.pbix)", type=["pbix"])

if uploaded_file is not None:
    # Ambil nama file asli tanpa ekstensi
    base_name = os.path.splitext(uploaded_file.name)[0]
    
    # PERBAIKAN: Parameter st.info disederhanakan agar tidak error
    st.info(f"Memproses file: **{uploaded_file.name}**...", icon="⏳")

    # Buat buffer di memori untuk menyimpan file ZIP hasil konversi
    zip_buffer = io.BytesIO()

    try:
        # Baca file .pbix sebagai file ZIP asli
        with zipfile.ZipFile(uploaded_file) as pbix_zip:
            
            # Buat ZIP baru yang akan didownload user
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as output_zip:
                
                # Daftar isi dari pbix
                namelist = pbix_zip.namelist()
                
                # Loop untuk memetakan isi pbix ke dalam struktur folder pbip
                for item in namelist:
                    file_data = pbix_zip.read(item)
                    
                    # Logika Pemetaan Struktur Folder PBIP:
                    if item.startswith("Report/"):
                        # Masuk ke folder .Report
                        new_path = item.replace("Report/", f"{base_name}.Report/")
                    elif item in ["DataModel", "DataMashup", "DiagramState"]:
                        # Masuk ke folder .SemanticModel
                        new_path = f"{base_name}.SemanticModel/{item}"
                    elif item == "Version":
                        # File versi ditaruh di semantic model
                        new_path = f"{base_name}.SemanticModel/{item}"
                    else:
                        # File lainnya ditaruh di root folder utama
                        new_path = f"{base_name}/{item}"
                    
                    # Tulis file ke dalam ZIP baru
                    output_zip.writestr(new_path, file_data)
                
                # Tambahkan file utama '.pbip' kosong sebagai penanda project
                pbip_metadata = '{\n  "version": "1.0",\n  "settings": {}\n}'
                output_zip.writestr(f"{base_name}.pbip", pbip_metadata)

        # Kembalikan penunjuk buffer ke awal agar bisa dibaca saat download
        zip_buffer.seek(0)

        st.success("Konversi Berhasil! 🎉")
        
        # 2. Tombol Download
        st.download_button(
            label="🎁 Download File PBIP (.zip)",
            data=zip_buffer,
            file_name=f"{base_name}_pbip.zip",
            mime="application/zip"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengonversi file: {e}")
