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

# Function to create Sankey diagram
def create_sankey(df):
    if df.empty:
        return None  # Don't create the Sankey diagram if the dataframe is empty
    
    categories = df['Category'].unique()
    
    nodes = []
    links = []
    
    category_to_id = {}  # Mapping categories to unique ids
    subcategory_to_id = {}  # Mapping subcategories to unique ids within each category
    
    node_idx = 0  # Keep track of node index for creating unique nodes

    # Create nodes and links
    for category in categories:
        category_to_id[category] = node_idx
        nodes.append(category)  # Add the category as a node
        node_idx += 1
        
        category_data = df[df['Category'] == category]  # Filter data for this category
        for subcategory in category_data['Subcategory'].unique():
            subcategory_to_id[(category, subcategory)] = node_idx
            nodes.append(subcategory)  # Add subcategory as a node within the category
            node_idx += 1
            
            # Add link from category to subcategory
            for _, row in category_data[category_data['Subcategory'] == subcategory].iterrows():
                links.append({
                    'source': category_to_id[category],
                    'target': subcategory_to_id[(category, subcategory)],
                    'value': row['Amount (AED)']
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

    fig.update_layout(title_text="Sankey Diagram of Budgeting Data", font_size=10)
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

            # Generate Sankey diagram
            fig = create_sankey(df_cleaned)
            if fig:
                st.plotly_chart(fig)
            else:
                st.write("Error: Sankey diagram could not be created.")

if __name__ == "__main__":
    main()
