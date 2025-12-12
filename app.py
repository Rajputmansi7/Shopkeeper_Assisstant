import streamlit as st
import os
import networkx as nx
import matplotlib.pyplot as plt
from graph_builder import KnowledgeGraph
from reasoning_engine import ShopkeeperEngine

# --- 1. Instantiate the Graph & Engine (Cached) ---
@st.cache_resource
def load_engine():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "kg.json")
    
    kg = KnowledgeGraph(json_path)
    
    if len(kg.nodes) == 0:
        st.error(f"CRITICAL ERROR: Graph is empty. Could not find 'kg.json' at: {json_path}")
        st.stop()
        
    engine = ShopkeeperEngine(kg)
    return engine

engine = load_engine()

# --- 2. Streamlit UI ---
st.set_page_config(page_title="Shopkeeper Assistant", layout="wide")
st.title("🛒 Shopkeeper Assistant")
st.markdown("Knowledge Graph-based product substitution.")

# Create Tabs
tab1, tab2 = st.tabs(["🔍 Find Substitutes", "🕸️ Visualize Graph"])

# ==========================================
# TAB 1: SEARCH INTERFACE (Core Assignment)
# ==========================================
with tab1:
    # Sidebar for Debugging
    st.sidebar.header("Database Status")
    st.sidebar.write(f"Total Nodes: {len(engine.kg.nodes)}")
    
    product_list = [d.get('label') or d.get('name') for n, d in engine.kg.nodes.items() if d.get('type')=='product']
    product_list.sort()

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        input_mode = st.radio("Input Method:", ["Select from List", "Type Manually"], horizontal=True)
        if input_mode == "Select from List" and product_list:
            product_name = st.selectbox("Select Product", product_list)
        else:
            product_name = st.text_input("Product Name", "Amul Taaza Fresh Milk")
    
    with col2:
        max_price = st.number_input("Max Price (₹)", min_value=1, value=50)

    tag_options = {
        "Vegetarian": "attr_veg",
        "Lactose Free": "attr_lactose_free",
        "Sugar Free": "attr_sugar_free",
        "Low Fat": "attr_low_fat"
    }
    selected_tags_labels = st.multiselect("Required Attributes", list(tag_options.keys()), default=["Vegetarian"])
    required_tags = [tag_options[label] for label in selected_tags_labels]

    optional_brand = st.selectbox("Preferred Brand (Optional)", ["None", "brand_amul", "brand_nestle", "brand_coke", "brand_pepsi", "brand_lays"])
    brand_input = None if optional_brand == "None" else optional_brand

    # Search Button
    st.divider()
    if st.button("Find Alternatives", type="primary"):
        if not product_name:
            st.error("Please provide a product name.")
        else:
            with st.spinner("Searching Knowledge Graph..."):
                result = engine.find_substitutes(
                    product_name=product_name,
                    max_price=max_price,
                    required_tags=required_tags,
                    optional_brand=brand_input
                )
                
                if result['status'] == 'found':
                    item = result['data']
                    display_name = item.get('label') or item.get('name')
                    st.success(f"✅ In Stock: {display_name}")
                    st.write(f"**Price:** ₹{item['price']}")
                    
                elif result['status'] == 'substitutes':
                    st.warning(f"❌ '{product_name}' is Out of Stock.")
                    st.info("💡 Here are the best rule-based alternatives:")
                    
                    for item in result['data']:
                        prod = item['product']
                        display_name = prod.get('label') or prod.get('name')
                        with st.expander(f"{display_name} - ₹{prod['price']}", expanded=True):
                            st.write(f"**Reason:** {item['explanation']}")
                            st.write(f"**Score:** {item['score']}")
                            
                else:
                    st.error("🚫 No suitable alternatives found.")
                    st.write(result.get('message', ''))

# ==========================================
# TAB 2: VISUALIZE GRAPH (Bonus)
# ==========================================
with tab2:
    st.header("Knowledge Graph Visualization")
    st.caption("Visualizing Nodes (Products, Categories, Brands) and Edges.")
    
    if st.button("Generate Graph Visualization"):
        with st.spinner("Drawing Graph..."):
            # 1. Create a NetworkX graph from our data
            G_vis = nx.Graph()
            
            # Add Nodes with Colors
            color_map = []
            for node_id, data in engine.kg.nodes.items():
                G_vis.add_node(node_id, label=data.get('label', node_id))
                
                # Assign colors based on type
                if data.get('type') == 'product': color_map.append('skyblue')
                elif data.get('type') == 'category': color_map.append('lightgreen')
                elif data.get('type') == 'brand': color_map.append('orange')
                elif data.get('type') == 'attribute': color_map.append('pink')
                else: color_map.append('grey')

            # Add Edges
            for node_id, neighbors in engine.kg.adj_list.items():
                for neighbor in neighbors:
                    G_vis.add_edge(node_id, neighbor['target'])

            # 2. Draw using Matplotlib
            fig, ax = plt.subplots(figsize=(12, 8))
            pos = nx.spring_layout(G_vis, k=0.3) # k adjusts spacing
            
            nx.draw(G_vis, pos, with_labels=True, node_color=color_map, 
                    node_size=2000, font_size=8, edge_color="gray", ax=ax)
            
            st.pyplot(fig)