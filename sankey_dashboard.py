import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to load and clean data
def load_and_clean_data(file):
    df = pd.read_excel(file, sheet_name='Total')
    df_cleaned = df[['Month', 'Category', 'Subcategory', 'Amount (AED)']].dropna()
    return df_cleaned

# Function to create Sankey diagram
def create_sankey(df):
    # Prepare data for Sankey diagram
    categories = df['Category'].unique()
    subcategories = df['Subcategory'].unique()
    
    category_to_id = {cat: idx for idx, cat in enumerate(categories)}
    subcategory_to_id = {sub: len(categories) + idx for idx, sub in enumerate(subcategories)}

    nodes = list(categories) + list(subcategories)
    links = []

    for _, row in df.iterrows():
        category_id = category_to_id[row['Category']]
        subcategory_id = subcategory_to_id[row['Subcategory']]
        links.append({'source': category_id, 'target': subcategory_id, 'value': row['Amount (AED)']})

    # Create Sankey diagram
    link_data = [link for link in links]
    node_data = [{'label': node, 'color': 'blue' if i < len(categories) else 'green'} for i, node in enumerate(nodes)]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=[node['label'] for node in node_data],
            color=[node['color'] for node in node_data]
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
        st.write("Data preview:")
        st.dataframe(df_cleaned.head())

        # Generate Sankey diagram
        fig = create_sankey(df_cleaned)
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
