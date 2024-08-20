import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Define function to load data
@st.cache_data
def load_data(region, platform='iOS'):
    try:
        # Define the directory where the files are located
        data_directory = './comb/'

        # Define the file names to look for based on region and platform
        file_mapping = {
            'United Arab Emirates': {
                'iOS': 'uae_iphone_games.csv',
                'Android': 'uae_android_games.csv'
            },
            'Saudi Arabia': {
                'iOS': 'saudi_iphone_games.csv',
                'Android': 'saudi_android_games.csv'
            },
            'Egypt': {
                'iOS': 'egypt_iphone_games.csv',
                'Android': 'egypt_android_games.csv'
            },
            'Iraq': {
                'iOS': 'iraq_iphone_games.csv',
                'Android': 'iraq_android_games.csv'
            },
            'Morocco': {
                'iOS': 'morocco_iphone_games.csv',
                'Android': 'morocco_android_games.csv'
            }
        }

        if region in file_mapping:
            platform_file = file_mapping[region].get(platform)
            if platform_file:
                selected_file = os.path.join(data_directory, platform_file)
                if os.path.exists(selected_file):
                    df = pd.read_csv(selected_file)
                    df.columns = df.columns.str.strip()  # Strip spaces from column names
                    return df
                else:
                    st.error(f"File not found: {selected_file}")
                    return pd.DataFrame()

        st.error(f"No files found for {region} ({platform}).")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of other errors

st.sidebar.write("Top rank data")
# Sidebar for platform selection
st.sidebar.title("Select Platform")
platform = st.sidebar.radio("Select Platform", ['iOS', 'Android'])

# Sidebar for region selection
st.sidebar.title("Select Region")
region = st.sidebar.radio("Select Region", ['United Arab Emirates', 'Saudi Arabia', 'Egypt',])

# Load the default data based on selected region and platform
default_data_df = load_data(region, platform=platform)

uploaded_file = st.sidebar.file_uploader(f"Choose a CSV file for {region} ({platform})", type="csv")

# Determine which data to use: default or uploaded
if uploaded_file is not None:
    data_df = pd.read_csv(uploaded_file)
    st.sidebar.success("CSV file successfully uploaded.")
    use_uploaded = st.sidebar.radio("Select Data Source", ['Use Uploaded File', 'Use Default File'])
    if use_uploaded == 'Use Default File' and not default_data_df.empty:
        data_df = default_data_df
else:
    if not default_data_df.empty:
        data_df = default_data_df
    else:
        st.warning(f"Default file not found for {platform} in {region}. Please upload a CSV file.")
        data_df = pd.DataFrame()  # Ensure data_df is initialized as an empty DataFrame

# Clear any remaining warnings or errors after data is loaded
if not data_df.empty:
    st.empty()  # Clears any previous warnings or errors
    st.sidebar.empty()  # Clears the sidebar of warnings

# Option to show/hide detailed view
show_detailed_view = st.sidebar.checkbox("Show Detailed View", True)

# Check if the necessary columns exist
required_columns = ['Category', 'Game Name', 'Rating', 'Position']
if not all(col in data_df.columns for col in required_columns):
    st.error(f"CSV file does not contain required columns: {', '.join(required_columns)}.")
else:
    # Sidebar for number of games to display with max set to number of rows in the file
    max_games = len(data_df)
    st.sidebar.title("Select number of top games to display")
    num_games = st.sidebar.slider("Select number of top games to display", 5, min(25, max_games), min(10, max_games))

    # Function to create bar charts using Seaborn with dark theme
    def create_bar_chart(df, title, x_col, y_col):
        if df.empty:
            st.warning(f"No data available for {title}")
            return
        
        plt.figure(figsize=(10, 6))
        sns.set(style="darkgrid")
        sns.set_palette("viridis")
        ax = sns.barplot(x=x_col, y=y_col, data=df.head(num_games), palette='viridis')
        ax.set_facecolor('#303030')
        plt.title(title, color='white')
        plt.xlabel(x_col, color='white')
        plt.ylabel(y_col, color='white')
        plt.xticks(color='white')
        plt.yticks(color='white')
        plt.gca().patch.set_facecolor('#303030')
        plt.gcf().set_facecolor('#303030')
        st.pyplot(plt)

    # Function to filter data by multiple possible category names
    def filter_data_by_category(df, categories):
        return df[df['Category'].isin(categories)]
    
    # Streamlit app layout
    st.title(f'Top {platform} Ranked Games by Category in {region}')

    # Define possible categories
    free_categories = ['Top Free Games', 'Free', 'Top Free']
    paid_categories = ['Top Paid Games', 'Paid', 'Top Paid' ]
    grossing_categories = ['Top Grossing Games', 'Grossing', 'Top Grossing']

    # Top Free Games and Top Paid Games in the first column
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Top Free Games")
        free_data = filter_data_by_category(data_df, free_categories)
        create_bar_chart(free_data, 'Top Free Apps', 'Position', 'Game Name')

        st.write("### Top Paid Games")
        paid_data = filter_data_by_category(data_df, paid_categories)
        create_bar_chart(paid_data, 'Top Paid Apps', 'Position', 'Game Name')

    # Top Grossing Games and Game Name by Rating in the second column
    with col2:
        st.write("### Top Grossing Games")
        grossing_data = filter_data_by_category(data_df, grossing_categories)
        create_bar_chart(grossing_data, 'Top Grossing Apps', 'Position', 'Game Name')

        st.write("### Game Name by Rating")
        create_bar_chart(data_df, 'Game Name by Rating', 'Rating', 'Game Name')

    if show_detailed_view:
        # Display columns of the uploaded CSV file
        st.write("### Detailed View all")
        st.dataframe(data_df)

    # Adding interactive filters
    category_options = data_df['Category'].unique()
    if len(category_options) > 0:
        category = st.selectbox('Select Category', category_options)
        filtered_category_df = data_df[data_df['Category'] == category]
        
        # Displaying detailed tables
        if show_detailed_view:
            st.write(f"### Detailed View: {category}")
            st.dataframe(filtered_category_df.head(num_games))
        
        # Creating bar chart for the selected category
        create_bar_chart(filtered_category_df, f'{category}', 'Position', 'Game Name')
        
        # Creating pie charts for distribution of ratings
        def create_pie_chart(df, title):
            if df.empty:
                st.warning(f"No data available for {title}")
                return
            
            rating_counts = df['Rating'].value_counts()
            plt.figure(figsize=(8, 8))
            plt.pie(rating_counts, labels=rating_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('plasma'))
            plt.title(title, color='white')
            plt.gca().patch.set_facecolor('#303030')
            plt.gcf().set_facecolor('#303030')
            for text in plt.gca().texts:
                text.set_color('white')  # Set pie chart text color to white
            # Adjust the color of the outer labels
            for text in plt.gca().texts[-len(rating_counts):]:
                text.set_color('white')
            st.pyplot(plt)
        
        st.write(f"### Rating Distribution for {category}")
        create_pie_chart(filtered_category_df.head(num_games), f'{category} Rating Distribution')
    else:
        st.write("No categories available in the selected dataset.")

st.info("build by dw v1 8/19/24")
st.success("Data successfully loaded from the first available file")
st.warning("Ensure that the file names match the expected names for each region and platform")