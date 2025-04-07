import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to load and clean data
def load_and_clean_data(file):
    try:
        df = pd.read_excel(file, sheet_name='Total')
        df_cleaned = df[['Month', 'Category', 'Subcategory', 'Amount (AED)']].dropna()
        st.write(f"Data loaded successfully. {len(df_cleaned)} records found.")
        return df_cleaned
    except Exception as e:
        st.write(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty dataframe on error

# Function to calculate total spend, category amounts, and percentages
def calculate_amounts_and_percentages(df):
    total_spend = df['Amount (AED)'].sum()
    category_sums = df.groupby('Category')['Amount (AED)'].sum()
    category_percentages = category_sums / total_spend * 100
    subcategory_sums = df.groupby(['Category', 'Subcategory'])['Amount (AED)'].sum()
    subcategory_percentages = subcategory_sums / total_spend * 100
    return total_spend, category_sums, category_percentages, subcategory_sums, subcategory_percentages

# Function to create Sankey diagram
def create_sankey(df, category_sums, subcategory_sums, total_spend):
    categories = df['Category'].unique()
    
    nodes = ['Total Spend']  # Start with total spend as the first node
    links = []
    
    category_to_id = {}  # Mapping categories to unique ids
    subcategory_to_id = {}  # Mapping subcategories to unique ids within each category
    
    node_idx = 1  # Keep track of node index for creating unique nodes (starting after 'Total Spend')

    # Create nodes and links for categories
    for category in categories:
        category_to_id[category] = node_idx
        nodes.append(f'{category} ({category_sums[category]:.2f} AED, {category_sums[category] / total_spend * 100:.2f}%)')
        node_idx += 1
        
        # Add link from total spend to category
        links.append({
            'source': 0,  # Total Spend
            'target': category_to_id[category],
            'value': category_sums[category]
        })

        # Create nodes and links for subcategories within each category
        for subcategory in df[df['Category'] == category]['Subcategory'].unique():
            subcategory_to_id[(category, subcategory)] = node_idx
            nodes.append(f'{subcategory} ({subcategory_sums[category, subcategory]:.2f} AED, {subcategory_sums[category, subcategory] / total_spend * 100:.2f}%)')
            node_idx += 1
            
            # Add link from category to subcategory
            links.append({
                'source': category_to_id[category],
                'target': subcategory_to_id[(category, subcategory)],
                'value': subcategory_sums[category, subcategory]
            })

    # Prepare data for Sankey diagram
    link_data = [link for link in links]
    node_data = [{'label': node} for node in nodes]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=[node['label'] for node in node_data]
        ),
        link=dict(
            source=[link['source'] for link in link_data],
            target=[link['target'] for link in link_data],
            value=[link['value'] for link in link_data],
            color='rgba(0, 128, 255, 0.4)'
        )
    ))

    # Adjust the layout for better readability (increased height)
    fig.update_layout(
        title_text="Sankey Diagram of Budgeting Data",
        font_size=12,
        height=2400,  # Increased height
        width=1200,   # Width
        title_x=0.5  # Center the title
    )

    return fig

# Streamlit UI
def main():
    st.title("Budgeting App with Sankey Diagram")

    st.sidebar.header("Upload your Excel file")
    uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df_cleaned = load_and_clean_data(uploaded_file)
        if df_cleaned.empty:
            st.write("No data found in the uploaded file.")
        else:
            st.write("Data preview:")
            st.dataframe(df_cleaned.head())

            # Calculate total, category and subcategory amounts and percentages
            total_spend, category_sums, category_percentages, subcategory_sums, subcategory_percentages = calculate_amounts_and_percentages(df_cleaned)
            
            # Display the total spend
            st.write(f"**Total Spend:** {total_spend:.2f} AED")

            # Create Sankey diagram
            fig = create_sankey(df_cleaned, category_sums, subcategory_sums, total_spend)
            if fig:
                st.plotly_chart(fig)
            else:
                st.write("Error: Sankey diagram could not be created.")

if __name__ == "__main__":
    main()

