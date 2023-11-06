import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# Define the scope for accessing Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Load credentials from a JSON key file
credentials = ServiceAccountCredentials.from_json_keyfile_name(r'creds.json', scope)

# Authorize the client using the credentials
client = gspread.authorize(credentials)

# Open the 'consumer_complaint_formated' Google Sheet
spreadsheet = client.open('consumer_complaint_formated')

# Select a specific worksheet (assuming it's the first one - you can change the index if needed)
worksheet = spreadsheet.get_worksheet(0)

# Fetch all the data from the worksheet
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Set the page layout to wide
st.set_page_config(layout="wide")

# Create a Streamlit app
st.title("Consumer Financial Complaints Dashboard")

# Define filter for state (e.g., 'All States' or 'Colorado')
# Define a list of all available states
all_states = df['state'].unique()
state_options = ['All States'] + list(all_states) + ['Colorado']

# Create a state filter dropdown with all state options
state_filter = st.selectbox("Select State", state_options)

# Handle the case when 'All States' is selected
if state_filter == 'All States':
    df_filtered = df
else:
    df_filtered = df[df['state'] == state_filter]

# Create a container for KPIs with custom CSS
st.markdown(
    """
    <style>
    .kpi-box {
        border: 1px solid #d1d1d1;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

kpi_container = st.container()
with kpi_container:
    st.header("KPI Grid")
    total_complaints = df_filtered.shape[0]
    total_closed_complaints = df_filtered[df_filtered['company_response'].str.contains("Closed")].shape[0]
    timely_responded_complaints = df_filtered[df_filtered['timely'] == 'Yes'].shape[0]
    in_progress_complaints = df_filtered[df_filtered['company_response'] == 'In Progress'].shape[0]

    # Arrange the KPIs in a horizontal layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='kpi-box'>Total Number of Complaints</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-box'>{total_complaints}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='kpi-box'>Total Number of Complaints with Closed Status</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-box'>{total_closed_complaints}</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='kpi-box'>% of Timely Responded Complaints</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-box'>{round(timely_responded_complaints / total_complaints * 100, 2)}%</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='kpi-box'>Total Number of Complaints with In Progress Status</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-box'>{in_progress_complaints}</div>", unsafe_allow_html=True)

# Create a container for charts
chart_container = st.container()
with chart_container:
    st.header("Number of complain by product")
    product_complaints = df_filtered['product'].value_counts()

    # Arrange the charts in a horizontal layout
    col1, col2 = st.columns(2)
    col1.bar_chart(product_complaints, use_container_width=True)

    # Check if 'date_received' column is datetimelike, and convert if needed
    if 'date_received' in df_filtered and not pd.api.types.is_datetime64_any_dtype(df_filtered['date_received']):
        df_filtered['date_received'] = pd.to_datetime(df_filtered['date_received'])

    # Now you can use the .dt accessor
    df_filtered['Month_Year'] = df_filtered['date_received'].dt.to_period('M')
    monthly_complaints = df_filtered['Month_Year'].value_counts().sort_index()
    col2.line_chart(monthly_complaints, use_container_width=True)

# Create a filter for submitted via channel
channel_filter = st.selectbox("Select Submitted Via Channel", df_filtered['submitted_via'].unique())
channel_filtered_data = df_filtered[df_filtered['submitted_via'] == channel_filter]

# Create content arrangement for the charts
chart_container2 = st.container()
with chart_container2:
    st.header("Side By Side Charts")
    st.write(f"Number of Complaints Submitted Via {channel_filter}")

    # Arrange the charts in a horizontal layout
# Arrange the charts in a horizontal layout
    col1, col2 = st.columns(2)

# Create a pie chart for 'Number of Complaints Submitted'
    submitted_pie_data = df_filtered['submitted_via'].value_counts()
    col1.plotly_chart(px.pie(submitted_pie_data, names=submitted_pie_data.index, values=submitted_pie_data.values))

    fig = px.treemap(df_filtered, path=['issue', 'sub_issue'], values='complaint_id')
    col2.plotly_chart(fig)

# Footer
st.write("Designed by Raza")
