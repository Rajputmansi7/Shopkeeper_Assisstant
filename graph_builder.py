import json
from collections import defaultdict

class KnowledgeGraph:
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self.nodes = {}
        self.adj_list = defaultdict(list)  # Adjacency list: node_id -> list of (neighbor_id, relation)
        self.category_hierarchy = defaultdict(list) # specific index for category parents
        
        # Load and build immediately
        self._load_data()
        self._build_graph()

    def _load_data(self):
        # Loads raw data from JSON file
        try:
            with open(self.data_file_path, 'r') as f:
                self.raw_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File {self.data_file_path} not found.")
            self.raw_data = {"nodes": [], "links": []}

    def _build_graph(self):
        # 1. Populate Node Lookup
        for node in self.raw_data['nodes']:
            self.nodes[node['id']] = node

        # 2. Build Adjacency List (Undirected Graph)
        for link in self.raw_data['links']:
            source = link['source']
            target = link['target']
            relation = link['relation']

            # Add forward edge
            self.adj_list[source].append({'target': target, 'relation': relation})
            
            # Add reverse edge 
            self.adj_list[target].append({'target': source, 'relation': relation})

            if relation == "IS_A":
                if self.nodes.get(source, {}).get('type') == 'category':
                     self.category_hierarchy[source].append(target)

    def get_node(self, node_id):
        # Returns attributes of a specific node
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id):
        #Returns a list of neighbors for a given node.
        return self.adj_list.get(node_id, [])

    def get_products_by_category(self, category_id):
        # to fetch all products that 'IS_A' specific category.
        products = []
        neighbors = self.adj_list.get(category_id, [])
        for n in neighbors:
            # Check if the neighbor is a product and the relation was IS_A (incoming to category)
            node_info = self.nodes.get(n['target'])
            if node_info and node_info['type'] == 'product' and n['relation'] == 'IS_A':
                products.append(node_info)
        return products

# Test Block 
if __name__ == "__main__":
    kg = KnowledgeGraph("kg.json")
    
    print(f"Graph loaded with {len(kg.nodes)} nodes.")
    
    # Test Node Retrieval
    product_id = "p_amul_taaza"
    print(f"\nNode Info for {product_id}:")
    print(kg.get_node(product_id))

    # Test Neighbor Traversal
    print(f"\nNeighbors of {product_id}:")
    for neighbor in kg.get_neighbors(product_id):
        neighbor_name = kg.get_node(neighbor['target'])['label'] if 'label' in kg.get_node(neighbor['target']) else kg.get_node(neighbor['target'])['name']
        print(f"  --[{neighbor['relation']}]--> {neighbor_name} ({neighbor['target']})")