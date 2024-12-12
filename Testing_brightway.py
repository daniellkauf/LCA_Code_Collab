# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# -*- coding: utf-8 -*-
"""
Brightway2 Setup Script 
"""

import bw2io as bi
import bw2calc as bc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

 #%%
import bw2data as bd


# Reinitialize Brightway2
bd.projects.create_project("dairy_lca", overwrite=True)
print("Brightway2 project reset.")



#%%

# Initialize system databases
bi.bw2setup()

print("Brightway2 environment initialized successfully.")


#%%
 

# Check if the database exists and delete it
if "Dairy" in bd.databases:
    del bd.databases["Dairy"]

# Re-register the Dairy database
dairy_db = bd.Database("Dairy")
dairy_db.register()


print("Dairy database registered.")

 
 #%%
import bw2data as bd
import bw2io as bi

 # Step 3: Add Dairy Activities

# Initialize system databases
bi.bw2setup()

print("Brightway2 environment initialized successfully.")

# Define the main processes
milk_production = dairy_db.new_activity(name="Milk Production", code="milk_production", type="process")
milk_production.save()

feed_production = dairy_db.new_activity(name="Feed Production", code="feed_production", type="process")
feed_production.save()

composting = dairy_db.new_activity(name="Composting", code="composting", type="process")
composting.save()

field_application = dairy_db.new_activity(name="Field Application", code="field_application", type="process")
field_application.save()

print("Processes defined.")
print("Available databases:", bd.databases)


#%%

# Define products

milk = dairy_db.new_activity(name="Milk", code="milk", type="product")
milk.save()

feed = dairy_db.new_activity(name="Feed", code="feed", type="product")
feed.save()

manure = dairy_db.new_activity(name="Manure", code="manure", type="product")
manure.save()

compost = dairy_db.new_activity(name="Compost", code="compost", type="product")
compost.save()

print("Products defined.")


#%%

biosphere = bd.Database("biosphere3")

# Define biosphere inputs and emissions 

methane_emission = biosphere.new_activity(name="Methane emission", code="CH4", type="process", categories=("air", "agriculture"))
methane_emission.save()

nitrous_oxide = biosphere.new_activity(name="Nitrous oxide emission", code="N2O", type="process", categories=("air", "agriculture"))
nitrous_oxide.save()

ammonia = biosphere.new_activity(name="Ammonia emission", code="NH3", type="process", categories=("air", "agriculture"))
ammonia.save()

nitrate_runoff = biosphere.new_activity(name="Nitrate runoff", code="NO3", type="process", categories=("water", "agriculture"))
nitrate_runoff.save()

carbon_dioxide = biosphere.new_activity(name="Carbon dioxide emission", code="CO2", type="process", categories=("air", "fossil"))
carbon_dioxide.save()

water_input = biosphere.new_activity(name="Water withdrawal", code="water", type="process", categories=("natural resource", "water"))
water_input.save()

diesel = biosphere.new_activity(name="Diesel use", code="diesel", type="process", categories=("natural resource", "fossil fuel"))
diesel.save()

print("Biosphere inputs and emissions added.")


#%%

# adding exchange to processes

# Milk Production
milk_production.new_exchange(input=feed, type="technosphere", amount=40).save()  # Feed input
milk_production.new_exchange(input=water_input, type="biosphere", amount=1000).save()  # Water input
milk_production.new_exchange(input=milk, type="production", amount=100).save()  # Produces milk
milk_production.new_exchange(input=manure, type="production", amount=50).save()  # Produces manure
milk_production.new_exchange(input=methane_emission, type="biosphere", amount=250).save()  # CH₄ emissions
milk_production.new_exchange(input=manure, type="production", amount=50).save()  # Manure produced by milk production

# Feed Production
feed_production.new_exchange(input=diesel, type="biosphere", amount=20).save()  # Diesel use
feed_production.new_exchange(input=water_input, type="biosphere", amount=500).save()  # Water use
feed_production.new_exchange(input=compost, type="technosphere", amount=30).save()  # Compost input
feed_production.new_exchange(input=feed, type="production", amount=40).save()  # Produces feed
feed_production.new_exchange(input=carbon_dioxide, type="biosphere", amount=50).save()  # Diesel-related CO₂ 

# Field Application
field_application.new_exchange(input=compost, type="technosphere", amount=30).save()  # Compost input
field_application.new_exchange(input=nitrous_oxide, type="biosphere", amount=10).save()  # N₂O emissions
field_application.new_exchange(input=ammonia, type="biosphere", amount=5).save()  # NH₃ emissions
field_application.new_exchange(input=nitrate_runoff, type="biosphere", amount=8).save()  # NO₃ runoff


# Composting consumes manure and produces compost
composting.new_exchange(input=manure, type="technosphere", amount=50).save()  # Manure input
composting.new_exchange(input=compost, type="production", amount=30).save()  # Compost output

#%%

# Define the functional unit
# Example: 1 unit of milk production as the reference flow
functional_unit = {milk: 1}

# Perform an LCA
lca = bc.LCA(functional_unit)
lca.lci()

# Access the matrices
technosphere_matrix = lca.technosphere_matrix.todense()
biosphere_matrix = lca.biosphere_matrix.todense()

# Display matrix shapes
print("Technosphere Matrix Shape:", technosphere_matrix.shape)
print("Biosphere Matrix Shape:", biosphere_matrix.shape)

# Visualize the Technosphere Matrix
plt.figure(figsize=(10, 8))
plt.title("Technosphere Matrix")
plt.imshow(technosphere_matrix, cmap="viridis", aspect="auto")
plt.colorbar(label="Flow Intensity")
plt.xlabel("Columns (Processes)")
plt.ylabel("Rows (Products)")
plt.show()

# Visualize the Biosphere Matrix
plt.figure(figsize=(10, 8))
plt.title("Biosphere Matrix")
plt.imshow(biosphere_matrix, cmap="magma", aspect="auto")
plt.colorbar(label="Impact Intensity")
plt.xlabel("Columns (Processes)")
plt.ylabel("Rows (Biosphere Flows)")
plt.show()



#%%
for activity in dairy_db:
    print(f"Activity: {activity['name']}")
    for exc in activity.exchanges():
        print(f"  Exchange: {exc.input['name']} ({exc['type']}): {exc['amount']}")

#%%
# Define node colors for all nodes, including processes, products, and biosphere flows
node_colors = {}

# Processes (Skyblue)
processes = ["Milk Production", "Feed Production", "Composting", "Field Application"]
for node in processes:
    node_colors[node] = "skyblue"

# Products (Lightgreen)
products = ["Milk", "Feed", "Manure", "Compost"]
for node in products:
    node_colors[node] = "lightgreen"

# Emissions and Inputs (Salmon)
biosphere_flows = [
    "Methane emission", "Nitrous oxide emission", "Ammonia emission",
    "Nitrate runoff", "Carbon dioxide emission", "Water withdrawal", "Diesel use"
]

for node in biosphere_flows:
    node_colors[node] = "salmon"
    
import networkx as nx
import matplotlib.pyplot as plt

# Initialize a directed graph
G = nx.DiGraph()

# Add nodes
all_nodes = processes + products + biosphere_flows
for node in all_nodes:
    G.add_node(node, type=node_colors[node])

# Add edges with flow amounts and units
edges_with_units = [
    ("Feed", "Milk Production", "40 kg"),
    ("Milk Production", "Milk", "100 L"),
    ("Milk Production", "Manure", "50 kg"),
    ("Milk Production", "Methane emission", "250 kg CH₄"),
    ("Water withdrawal", "Milk Production", "1000 L"),
    ("Diesel use", "Feed Production", "20 L"),
    ("Water withdrawal", "Feed Production", "500 L"),
    ("Compost", "Feed Production", "30 kg"),
    ("Feed Production", "Feed", "40 kg"),
    ("Feed Production", "Carbon dioxide emission", "50 kg CO₂"),
    ("Manure", "Composting", "50 kg"),
    ("Composting", "Compost", "30 kg"),
    ("Composting", "Methane emission", "5 kg CH₄"),
    ("Composting", "Nitrous oxide emission", "3 kg N₂O"),
    ("Compost", "Field Application", "30 kg"),
    ("Field Application", "Nitrous oxide emission", "10 kg N₂O"),
    ("Field Application", "Ammonia emission", "5 kg NH₃"),
    ("Field Application", "Nitrate runoff", "8 kg NO₃")
]

# Add edges to the graph
for source, target, label in edges_with_units:
    G.add_edge(source, target, label=label)

# Generate positions using spring layout
pos = nx.spring_layout(G, seed=42)

# Draw the graph
plt.figure(figsize=(14, 10))

# Draw nodes with colors
nx.draw_networkx_nodes(
    G, pos,
    node_color=[node_colors[node] for node in G.nodes()],
    node_size=3000,
    alpha=0.9
)

# Draw edges without scaling width
nx.draw_networkx_edges(G, pos, edge_color="gray", alpha=0.7)

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")

# Add edge labels (flow amounts with units)
edge_labels = {(u, v): f"{d['label']}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

# Title and legend
plt.title("Dairy System Network Visualization with Units", fontsize=16)
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='Process', markerfacecolor='skyblue', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='Product', markerfacecolor='lightgreen', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='Emission/Input', markerfacecolor='salmon', markersize=10)
]
plt.legend(handles=legend_elements, loc='upper left', fontsize=10)

plt.axis("off")
plt.show()




