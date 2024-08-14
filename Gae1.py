import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define function to load data
@st.cache_data
def load_data(region, file_path=None, platform='iOS'):
    try:
        if region == 'United Arab Emirates' and file_path is None:
            # Use default data for UAE
            default_file_path = f't25-uae-{platform.lower()}.csv'
            df = pd.read_csv(default_file_path)
        elif file_path:
            df = pd.read_csv(file_path)
        else:
            st.error("Please upload a CSV file for the selected region.")
            return pd.DataFrame()
        df.columns = df.columns.str.strip()  # Strip spaces from column names
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Sidebar for platform selection
st.sidebar.title("Select Platform")
platform = st.sidebar.radio("Select Platform", ['iOS', 'Android'])

# Sidebar for region selection
st.sidebar.title("Select Region")
region = st.sidebar.radio("Select Region", ['United Arab Emirates', 'Saudi Arabia', 'Egypt', 'Iraq', 'Morocco'])

uploaded_file = None
if region != 'United Arab Emirates':
    uploaded_file = st.sidebar.file_uploader(f"Choose a CSV file for {region} ({platform})", type="csv")

data_df = load_data(region, uploaded_file, platform)

# Option to show/hide detailed view
show_detailed_view = st.sidebar.checkbox("Show Detailed View", True)

# Check if the necessary columns exist
required_columns = ['Category', 'Game Name', 'Rating', 'Position']
if not all(col in data_df.columns for col in required_columns):
    st.error(f"CSV file does not contain required columns: {', '.join(required_columns)}.")
else:
    # Sidebar for number of games to display
    st.sidebar.title("Select number of top games to display")
    num_games = st.sidebar.slider("Select number of top games to display", 5, 25, 10)

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
    free_categories = ['Top Free Apps', 'Free']
    paid_categories = ['Top Paid Apps', 'Paid']
    grossing_categories = ['Top Grossing Apps', 'Grossing']

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

st.info("build by dw v1 8/14/24")
