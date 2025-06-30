import streamlit as st
import os
import gdown
import easyocr
import tempfile
import time
from PIL import Image
from parse_lottery import parse_ticket
from lottery_api import get_latest_powerball, get_latest_megamillions

MODEL_DIR = "/mount/src/luckysnap/models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Model files with public shareable links
MODEL_FILES = {
    "craft_mlt_25k.pth": "https://drive.google.com/file/d/1irGU6W6Y0pUfy4FVm-Q1-QY1AQ1E4pf1/view?usp=sharing",
    "english_g2.pth": "https://drive.google.com/file/d/1nlQ5bvqX7p6KztQaeVoGvePJsCPieTxS/view?usp=sharing"}

# Download the models if not already present
def ensure_model_file(filename, url):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        st.write(f"📥 Downloading {filename}...")
        gdown.download(url, path, fuzzy=True, quiet=False)
        st.success(f"✅ Downloaded {filename}")
    return path

for fname, link in MODEL_FILES.items():
    ensure_model_file(fname, link)

st.set_page_config(page_title="Lottery Ticket Checker", page_icon="🎟️", layout="centered")
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🎟️ Lottery Ticket Checker</h1>
    <p style='text-align: center; font-size: 18px;'>Snap it. Check it. Win it!</p>
""", unsafe_allow_html=True)

@st.cache_resource
def get_reader():
    return easyocr.Reader(['en'], gpu=False, model_storage_directory=MODEL_DIR, download_enabled=False)

reader = get_reader()

# Step 1: Select game type
game_type = st.selectbox("Select Lottery Game", ["Mega Millions", "Powerball"])

# Step 2: Upload image
uploaded_file = st.file_uploader("📸 Upload Your Ticket Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # 🧠 Limit image size to avoid crashing OCR
    MAX_DIM = 1280
    image.thumbnail((MAX_DIM, MAX_DIM))

    st.image(image, caption="📸 Uploaded Ticket", use_container_width=True)

    with st.spinner("🔍 Extracting Text with OCR..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image.save(tmp.name)
            start_time = time.time()
            result = reader.readtext(tmp.name, detail=0, paragraph=True)
            ocr_text = " ".join(result)
            duration = time.time() - start_time

    st.caption(f"OCR completed in {duration:.2f}s")

    with st.expander("📝 Raw OCR Text"):
        st.text(ocr_text)

    # Step 3: Parse ticket and extract draw date
    ticket_rows, ticket_date = parse_ticket(ocr_text, game_type)

    if not ticket_rows:
        st.error("❌ Could not find valid numbers on this ticket.")
        st.stop()

    if not ticket_date:
        st.warning("⚠️ Could not detect draw date from ticket. Please ensure the date is clearly printed.")
        st.stop()

    st.success(f"🗓️ Ticket Draw Date Detected: {ticket_date}")

    # Step 4: Fetch official draw numbers
    try:
        if game_type == "Powerball":
            (official_numbers, special_ball), official_date = get_latest_powerball(return_with_date=True)
        else:
            (official_numbers, special_ball), official_date = get_latest_megamillions(return_with_date=True)

    except Exception as e:
        st.error("❌ Failed to fetch official winning numbers.")
        st.exception(e)
        st.stop()

    st.info(f"🎯 Recent Draw Date: {official_date}")

    if str(ticket_date).strip() != str(official_date).strip():
        st.warning("⚠️ Ticket draw date does not match the latest official draw. Please verify the ticket.")
        st.stop()

    st.success("✅ Ticket date matches the official draw!")
    st.subheader("🎯 Official Winning Numbers")

    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Main Numbers:** `{', '.join(map(str, official_numbers))}`")

    with cols[1]:
        special_label = "Mega Ball" if game_type == "Mega Millions" else "Powerball"
    st.markdown(f"**{special_label}:** `{special_ball}`")

        # Step 5: Compare numbers
    st.subheader("🏁 Match Results")
    st.write(f"Detected {len(ticket_rows)} line(s) on the ticket.")

    for i, row in enumerate(ticket_rows):
        matched = len(set(row["numbers"]) & set(official_numbers))
        special_matched = False

        if game_type == "Mega Millions":
            special_matched = row.get("megaball") == special_ball
        else:
            special_matched = row.get("powerball") == special_ball

        with st.container():
            st.markdown(f"**Line {i+1}** 🎟️")
            st.markdown(f"- Numbers: `{row['numbers']}`")
            st.markdown(f"- Special: `{row.get('powerball') or row.get('megaball')}`")
            st.markdown(f"- Matched: `{matched}` {'+ Special!' if special_matched else ''}")

            if matched >= 3 or special_matched:
                st.success(f"✅ {matched} numbers matched" + (" + special ball" if special_matched else ""))
            else:
                st.error(f"❌ Only {matched} numbers matched")
