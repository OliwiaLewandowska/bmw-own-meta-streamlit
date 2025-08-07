
import streamlit as st
import pandas as pd
import os
from PIL import Image
import glob


# Load metadata
import ast
df = pd.read_csv('bmw_models.csv')

# Parse image_names and video_names columns (convert stringified lists to lists)
for col in ['image_names', 'video_names']:
    df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) and x.startswith('[') else [])

# Create a long-form DataFrame: one row per image or video
media_rows = []
for _, row in df.iterrows():
    for img in row['image_names']:
        if img != 'no_images_found':
            r = row.copy()
            r['media_type'] = 'image'
            r['media_file'] = img
            media_rows.append(r)
    for vid in row['video_names']:
        if vid != 'no_videos_found':
            r = row.copy()
            r['media_type'] = 'video'
            r['media_file'] = vid
            media_rows.append(r)
media_df = pd.DataFrame(media_rows)

# Path to data_models folder
DATA_FOLDER = 'data_models'

# Helper: get all media files (images/videos)
def get_media_files(folder):
    exts = ['*.jpg', '*.jpeg', '*.png', '*.mp4', '*.mov']
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(folder, ext)))
    return sorted(files)

media_files = get_media_files(DATA_FOLDER)


# Map file basename to full path for quick lookup
media_map = {os.path.basename(f): f for f in media_files}



# Sidebar filter
st.sidebar.title('Filters')
countryids = ['All'] + sorted(media_df['countryid'].dropna().unique())
selected_country = st.sidebar.selectbox('Select countryid', countryids)

model_labels = ['All'] + sorted(media_df['model_label'].dropna().unique())
selected_model = st.sidebar.selectbox('Select model', model_labels, key='model_label')

# Filter dataframe
filtered_df = media_df.copy()
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['countryid'] == selected_country]
if selected_model != 'All':
    filtered_df = filtered_df[filtered_df['model_label'] == selected_model]



# --- App Title and Style ---
st.markdown(
    """
    <style>
    .main-title {font-size:2.5em; font-weight:700; color:#003366; margin-bottom:0.2em;}
    .subtitle {font-size:1.3em; color:#666; margin-bottom:1em;}
    .reach-label {font-size:1.1em; color:#155724; font-weight:600; margin-bottom:0.2em;}
    .meta-label {font-size:1em; color:#333; margin-bottom:0.2em;}
    .stMetric {background: #f8f9fa; border-radius: 8px;}
    /* Reduce Streamlit default padding */
    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1200px;
    }
    /* Remove extra padding on main */
    section.main > div:first-child {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<div class="main-title">BMW Motorrad Media Visualisation</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Browse and analyze campaign media and performance</div>', unsafe_allow_html=True)
st.markdown('---')

# --- Summary statistics ---
st.subheader('Summary Statistics')
avg_reach_per_model = filtered_df.groupby('model_label')['overall_reach'].mean().sort_values(ascending=False)

cols = st.columns(min(4, len(avg_reach_per_model)))
for i, (model, avg_reach) in enumerate(avg_reach_per_model.items()):
    with cols[i % len(cols)]:
        st.metric(label=f"Avg Reach: {model}", value=f"{int(round(avg_reach)):,}")

st.markdown('---')



# --- Media browser ---
st.subheader('Media Gallery')

# Only show rows with a media file in data_models
filtered_df = filtered_df[filtered_df['media_file'].apply(lambda x: isinstance(x, str) and x in media_map)]

if filtered_df.empty:
    st.info('No media found for the selected filter.')
else:
    # Display all media in 3 columns
    n_cols = 3
    media_list = filtered_df.to_dict('records')
    cols = st.columns(n_cols)
    for idx, row in enumerate(media_list):
        with cols[idx % n_cols]:
            media_path = media_map[row['media_file']]
            if row['media_type'] == 'image':
                st.image(Image.open(media_path), use_container_width=True)
            elif row['media_type'] == 'video':
                st.video(media_path)
            # Model label
            st.markdown(f"<div class='meta-label'><b>Model:</b> {row.get('model_label','')}</div>", unsafe_allow_html=True)
            # Countryid
            st.markdown(f"<div class='meta-label'><b>Country:</b> {row.get('countryid','')}</div>", unsafe_allow_html=True)
            # Overall Reach
            reach_val = int(row['overall_reach']) if pd.notnull(row['overall_reach']) else '-'
            reach_str = f"{reach_val:,}" if reach_val != '-' else '-'
            st.markdown(f"<div class='reach-label'>Overall Reach: {reach_str}</div>", unsafe_allow_html=True)
            # Other metadata
            st.markdown(f"<div class='meta-label'><b>Date Range:</b> {row.get('date_range','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-label'><b>Ad Link:</b> <a href='{row.get('ad_link','')}' target='_blank'>{row.get('ad_link','')}</a></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-label'><b>Platforms:</b> {row.get('platforms','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-label'><b>Caption:</b> {row.get('caption','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-label'><b>CTA Caption:</b> {row.get('cta_caption','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='meta-label'><b>CTA Button:</b> {row.get('cta_button','')}</div>", unsafe_allow_html=True)
