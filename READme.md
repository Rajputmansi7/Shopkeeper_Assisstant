# 🛒 Shopkeeper Product Substitution Assistant

A **Knowledge Graph-based** AI assistant that suggests intelligent product substitutes when a requested item is out of stock.

This project implements **classical AI reasoning** (Graph Search + Rule-based Logic) without using Machine Learning, Embeddings, or LLMs, ensuring deterministic and explainable results.

### 🔗 **[Click Here to View Deployed App](https://shopk-assisstance.streamlit.app)**

-----

## 📖 Project Overview

When a customer asks for a product that is out of stock, a shopkeeper doesn't just say "No." They mentally traverse a graph of related items:

1.  *"Is there another brand of the same product?"* (e.g., Amul Milk → Nestle Milk)
2.  *"Is there a similar product in the same category?"* (e.g., Lays Chips → Pringles)
3.  *"Does it meet the customer's budget and dietary needs?"* (e.g., Sugar-free, Veg)

This application mimics that cognitive process using a **Knowledge Graph**.

-----

## 🕸️ Knowledge Graph Design

The backend data structure is a graph where **Nodes** represent entities and **Edges** represent relationships.

### **1. Nodes**

  * **Product:** The item being sold (e.g., "Amul Taaza Fresh Milk").
      * *Properties:* `price`, `in_stock`, `id`, `label`.
  * **Category:** Hierarchical grouping (e.g., "Milk", "Dairy", "Snacks").
  * **Brand:** Manufacturer (e.g., "Amul", "Pepsi").
  * **Attribute:** Dietary tags (e.g., "Vegetarian", "Sugar Free", "Lactose Free").

### **2. Edges (Relationships)**

  * `IS_A`: Connects a **Product** to its **Category** (e.g., *Coke* `IS_A` *Soda*).
  * `HAS_BRAND`: Connects a **Product** to a **Brand**.
  * `HAS_ATTRIBUTE`: Connects a **Product** to a feature (e.g., *Diet Coke* `HAS_ATTRIBUTE` *Sugar Free*).
  * `SIMILAR_TO`: Explicit connections between close substitutes (e.g., *Lays* `SIMILAR_TO` *Pringles*).

-----

## 🧠 Reasoning & Search Algorithm

The core logic is implemented in `reasoning_engine.py` using a **Breadth-First Search (BFS)** approach with filtering.

### **Step 1: Availability Check**

  * If the requested product is `in_stock = true`, return it immediately.

### **Step 2: Candidate Generation (Graph Traversal)**

If out of stock, the engine traverses the graph:

1.  **Level 1 Search:** Find all products connected to the **Same Category**.
2.  **Level 2 Search:** If fewer than 3 candidates are found, traverse up to the **Parent Category** and find "Sibling Categories" (e.g., Milk -\> Dairy -\> Yogurt).

### **Step 3: Filtering**

Candidates are rejected if they:

  * Are Out of Stock.
  * Exceed the user's `Max Price`.
  * Do not possess **all** `Required Attributes` (e.g., missing 'Sugar Free').

### **Step 4: Scoring & Ranking**

Valid candidates are scored to find the "best" match:

  * **+3 Points:** Same Category.
  * **+2 Points:** Direct `SIMILAR_TO` connection.
  * **+1 Point:** Similar (Sibling) Category.
  * **+1 Point:** Same Brand as original request.
  * **+1 Point:** Matches user's preferred Brand.
  * **+1 Point:** Cheaper than max budget.

-----

## 📝 Rule-Based Explanations

Instead of opaque ML scores, every suggestion comes with a human-readable explanation derived from the scoring rules:

| Condition | Generated Explanation |
| :--- | :--- |
| **Same Category** | *"Same Category"* |
| **Sibling Category** | *"Similar Category"* |
| **Brand Match** | *"Same Brand as requested"* |
| **Price Check** | *"Within Budget"* |
| **Graph Connection** | *"Directly Related"* |

-----

## 🛠️ Installation & Local Setup

To run this project on your local machine:

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/Rajputmansi7/shopkeeper-assistant.git
    cd shopkeeper-assistant
    ```

2.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**

    ```bash
    streamlit run app.py
    ```

4.  **Open Browser**
    Go to `http://localhost:8501`

-----

## 📂 File Structure

  * `app.py`: The frontend user interface (Streamlit). Handles user input and displays results.
  * `reasoning_engine.py`: The brain. Contains the search algorithms, filtering logic, and scoring system.
  * `graph_builder.py`: Loads the JSON data and constructs the graph (Adjacency List).
  * `kg.json`: The dataset containing all nodes and edges.
  * `requirements.txt`: List of Python libraries required.

-----

## 🧪 Example Test Cases

**Case 1: Dietary Restriction**

  * **Input:** "Coca Cola Classic" (Out of Stock), Tag: "Sugar Free".
  * **Result:** Suggests "Diet Coke".
  * **Reason:** Excludes "Pepsi" because it lacks the "Sugar Free" attribute node.

**Case 2: Brand Loyalty**

  * **Input:** "Nestle Slim Dahi" (Out of Stock), Brand Pref: "Amul".
  * **Result:** Suggests "Amul Masti Dahi".
  * **Reason:** High score due to `Category Match` + `Preferred Brand Match`.


### Author

**Mansi Singh**
