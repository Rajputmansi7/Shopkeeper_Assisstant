class ShopkeeperEngine:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def _normalize(self, text):
        if not text: 
            return ""
        return " ".join(text.strip().lower().split())

    def _get_product_id_by_name(self, name):
        target_slug = self._normalize(name)
        
        for node_id, data in self.kg.nodes.items():
            if data.get('type') == 'product':
                node_label = data.get('label') or data.get('name')
                if node_label:
                    # Compare normalized strings to avoid case/space errors
                    if self._normalize(node_label) == target_slug:
                        return node_id
        return None

    def _get_category_of_product(self, product_id):
        neighbors = self.kg.get_neighbors(product_id)
        for n in neighbors:
            if n['relation'] == 'IS_A' and self.kg.get_node(n['target'])['type'] == 'category':
                return n['target']
        return None

    def _get_attributes_of_product(self, product_id):
        attrs = set()
        neighbors = self.kg.get_neighbors(product_id)
        for n in neighbors:
            if n['relation'] == 'HAS_ATTRIBUTE':
                attrs.add(n['target']) 
        return attrs

    def _get_brand_of_product(self, product_id):
        neighbors = self.kg.get_neighbors(product_id)
        for n in neighbors:
            if n['relation'] == 'HAS_BRAND':
                return n['target']
        return None

    def find_substitutes(self, product_name, max_price, required_tags, optional_brand=None):
        
        #  Main Reasoning Function.
        # 1. Resolve Product ID
        target_id = self._get_product_id_by_name(product_name)
        if not target_id:
            return {"status": "not_found", "message": "Product not found in database. Please check the spelling or use the list selector."}

        target_node = self.kg.get_node(target_id)
        # display name
        target_display_name = target_node.get('label') or target_node.get('name')

        # Check Exact Availability
        if target_node.get('in_stock'):
            return {"status": "found", "data": target_node}

        # If Out of Stock -> Start Graph Search
        candidates = []
        target_category_id = self._get_category_of_product(target_id)
        target_brand_id = self._get_brand_of_product(target_id)
        
        if not target_category_id:
             return {"status": "not_found", "message": "Product has no category."}

        # Strategy A: Same Category Search
        same_cat_products = self.kg.get_products_by_category(target_category_id)
        for p in same_cat_products:
            if p['id'] != target_id: 
                candidates.append({
                    "node": p, 
                    "relation_type": "same_category",
                    "category_id": target_category_id
                })

        # Strategy B: Similar Category Search (Sibling Categories)
        # Only if we have fewer than 3 candidates
        if len(candidates) < 3:
            cat_neighbors = self.kg.get_neighbors(target_category_id)
            parent_cat_id = None
            for n in cat_neighbors:
                if n['relation'] == 'IS_A': 
                    parent_cat_id = n['target']
                    break
            
            if parent_cat_id:
                parent_neighbors = self.kg.get_neighbors(parent_cat_id)
                for n in parent_neighbors:
                    neighbor_node = self.kg.get_node(n['target'])
                    # Check if neighbor is a category and NOT the original category
                    if (neighbor_node['type'] == 'category' and n['target'] != target_category_id):
                        sibling_products = self.kg.get_products_by_category(n['target'])
                        for p in sibling_products:
                            candidates.append({
                                "node": p, 
                                "relation_type": "similar_category",
                                "category_id": n['target']
                            })

        # 4. Filtering & Scoring
        scored_results = []
        
        for cand in candidates:
            product = cand['node']
            p_id = product['id']
            
            # Filter 1: In Stock Only
            if not product.get('in_stock'):
                continue
            
            # Filter 2: Max Price
            if product.get('price') > max_price:
                continue

            # Filter 3: Required Attributes
            p_attrs = self._get_attributes_of_product(p_id)
            if not set(required_tags).issubset(p_attrs):
                continue
                
            # Scoring Logic
            score = 0
            reasons = []

            # Rule: Category Closeness
            if cand['relation_type'] == "same_category":
                score += 3
                reasons.append("Same Category")
            elif cand['relation_type'] == "similar_category":
                score += 1
                reasons.append("Similar Category")

            # Rule: Brand Match
            p_brand = self._get_brand_of_product(p_id)
            if optional_brand and p_brand == optional_brand:
                score += 1
                reasons.append("Requested Brand Match")
            elif p_brand == target_brand_id:
                score += 1
                reasons.append("Same Brand")

            # Rule: Attribute Overlap (Bonus)
            target_attrs = self._get_attributes_of_product(target_id)
            common_attrs = p_attrs.intersection(target_attrs)
            if len(common_attrs) > 0:
                score += len(common_attrs)

            # Rule: Price
            if product.get('price') < max_price:
                score += 1
                reasons.append("Within Budget")
            
            # Rule: Direct SIMILAR_TO Edge
            direct_neighbors = [n['target'] for n in self.kg.get_neighbors(target_id)]
            if p_id in direct_neighbors:
                score += 2
                reasons.append("Directly Related")

            scored_results.append({
                "product": product,
                "score": score,
                "explanation": ", ".join(reasons)
            })

        # 5. Sort and Return Top 3
        # Sort by score (descending), then by price (ascending)
        scored_results.sort(key=lambda x: (-x['score'], x['product']['price']))
        
        top_3 = scored_results[:3]
        
        if not top_3:
            return {"status": "not_found", "message": "No suitable alternatives found matching criteria."}
            
        return {"status": "substitutes", "data": top_3}