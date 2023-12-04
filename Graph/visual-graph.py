import os
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

class GraphVisualization:
    Graph = None
    directed = False # Default
    weighted = False # Default
    position = None

    def __init__(self):
        self.visual = []

    def status(self):
        print("Graph status: ")
        if VisualGraph.Graph != None:
            print(f"[Directed: {VisualGraph.directed}.]")
            print(f"[Weighted: {VisualGraph.weighted}.]")
        else:
            print("[Graph does not exist.]")

    def createGraph(self, directed=False, weighted=False):
        self.Graph = nx.DiGraph() if directed else nx.Graph()
        self.weighted = weighted
        self.directed = directed

        if self.weighted:
            self.Graph.add_weighted_edges_from(self.visual)
            edge_labels = nx.get_edge_attributes(self.Graph, 'weight')
        else:
            self.Graph.add_edges_from([(u, v) for u, v, _ in self.visual])
            edge_labels = None

        self.position = nx.spring_layout(self.Graph, seed=15)
        self.__draw(self.Graph, self.position, self.directed, edge_labels)

    def addEdge(self, a, b, weight=0.0):
        temp = (a, b, weight)
        print(f"[Added edge {a} {b} with weight {weight}].")
        self.visual.append(temp)

    def removeEdge(self, a, b):
        found = False
        for edge in self.visual:
            if a == edge[0] and b == edge[1]:
                found = True
                self.visual.remove(edge)
                break
        if not self.visual:
            self.Graph = None
            self.position = None
        print(f"[Removed edge {a} {b}].") if found else print(f"[Edge {a} {b} is undefined].")
            
    def reset(self):
        self.visual = []
        self.Graph = None
        self.directed = False
        self.weighted = False
        self.position = None
        print("[Resetted the whole graph.]")
       
    # Methods for traversing graph such as DFS and BFS.
    def __DFS(self, start_node) -> dict():
        visited = set(start_node)
        stack = list(start_node)
        traverse = list()

        path = 0
        result = {path: list()}

        while stack:
            node = stack.pop()
            traverse.append(node)

            neighbors = list(self.Graph.neighbors(node))
            neighbors.reverse()
            
            # Find the leaf node.
            if self.directed and (self.Graph.in_degree(node) == 1 and self.Graph.out_degree(node) == 0):
                for i in range(len(traverse) - 1, 0, -1):
                    if not self.Graph.has_successor(traverse[i - 1], traverse[i]):
                        traverse.remove(traverse[i - 1])
                
                if path not in result:
                    result[path] = list()
                for i in range(0, len(traverse)):
                    result[path].append(traverse[i])
                path += 1
            elif not self.directed and len(neighbors) == 1:
                for i in range(len(traverse) - 1, 0, -1):
                    if not self.Graph.has_edge(traverse[i - 1], traverse[i]):
                        traverse.remove(traverse[i - 1])

                if path not in result:
                    result[path] = list()
                for i in range(0, len(traverse)):
                    result[path].append(traverse[i])
                path += 1

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        return result
                
    def __BFS(self, start_node) -> [nx.DiGraph(), dict()]:
        visited = set(start_node)
        queue = [(start_node, 0)]
        traverse = {0: [start_node]}

        # BFS traversal.
        while queue:
            node, level = queue.pop(0)
            neighbors = list(self.Graph.neighbors(node))

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))
                
                    if level + 1 not in traverse:
                        traverse[level + 1] = []
                    traverse[level + 1].append(neighbor)
        
        bfs_tree = nx.DiGraph()

        root = traverse[0].pop() # Remove root node.
        edge_labels = {}

        foldername = "BFS_result"
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        for key, value in traverse.items():
            if key + 1 in traverse:
                next_level = key + 1
                next_node = traverse[next_level][0]
                bfs_tree.add_edge(root, next_node) # Connect root node to each level.
                edge_labels[(root, next_node)] = "Level " + str(next_level) # Edge labels to indicate level of nodes.

            # Form an edge between 2 nodes in the same level from left to right.
            for i in range(0, len(value) - 1):
                bfs_tree.add_edge(value[i], value[i + 1])
            pos = nx.spring_layout(bfs_tree, seed=15)
            
            # Draws nodes, edges, labels and edge labels.
            self.__draw(bfs_tree, pos, True, [])
            nx.draw_networkx_edge_labels(bfs_tree, pos, edge_labels=edge_labels, font_color='red')

            directory = f"{foldername}\path_{key}"
            if self.__save(directory):
                print(f"[Exported traverse progress number {key} to folder {foldername}].")
            else:
                print(f"[Failed to export traverse progress number {key} to folder {foldername}].")
        return [bfs_tree, edge_labels]
    
    # Shortest paths algorithms.
    def __result_from_source_to_vertices(self, source, vertices=dict()):
        result = {
            "Path": [],
            "Cost": []
        }
        for vertice, cost in vertices.items():
            path = f"{source}->{vertice}"
            result["Path"].append(path)
            result["Cost"].append(cost)
        
        indexes = [f"[{i}]" for i in range(0, len(vertices))]
        df = pd.DataFrame(result, index=indexes)
        print(df)

    def dijkstra(self):
        start_node = input("Start> ")
        # Inner function to find min node.
        def find_min_node(visited, distances):
            min_distance = float('inf')
            min_node = None

            for node in self.Graph.nodes():
                if node not in visited and distances[node] < min_distance:
                    min_distance = distances[node]
                    min_node = node
            return min_node
        
        distances = {}
        visited = []
        for node in self.Graph.nodes():
            distances[node] = float('inf')

        distances[start_node] = 0

        for i in range(0, len(self.Graph.nodes()) - 1):
            min_node = find_min_node(visited, distances)

            visited.append(min_node)

            # Update distances to neighbors.
            for neighbor in self.Graph.neighbors(min_node):
                distance_to_neighbor = distances[min_node] + self.Graph[min_node][neighbor].get('weight', 1)

                if distance_to_neighbor < distances[neighbor]:
                    distances[neighbor] = distance_to_neighbor
        self.__result_from_source_to_vertices(source=start_node, vertices=distances)

    def bellman_ford(self):
        start_node = input("Start> ")
        distances = {}
        for node in self.Graph.nodes():
            distances[node] = float('inf')

        distances[start_node] = 0

        edges = list(self.Graph.edges.data("weight", default=1))
        for _ in range(0, len(list(self.Graph.nodes())) - 1):    
            for u, v, w in edges:
                distance_to_neighbor = distances[u] + w
                if distances[u] != float("inf") and distance_to_neighbor < distances[v]:
                    distances[v] = distance_to_neighbor
            if not self.directed:
                for u, v, w in edges:
                    distance_to_neighbor = distances[v] + w
                    if distances[v] != float("inf") and distance_to_neighbor < distances[u]:
                        distances[u] = distance_to_neighbor
        
        # Check for negative weight cycle.
        for u, v, w in edges:
            distance_to_neighbor = distances[u] + w
            if distances[u] != float("inf") and distance_to_neighbor < distances[v]:
                print("[Graph contains negative-weight cycle.]")
                cycle = nx.find_negative_cycle(self.Graph, source=start_node, weight='weight')
                print(cycle)
                return None
        self.__result_from_source_to_vertices(source=start_node, vertices=distances)

    # Other interesting methods.
    def __save(self, save_as=None) -> bool():
        try:
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(save_as)
            plt.close()
            return True
        except Exception as e:
            print(f"[An error occured while trying to save a figure: {e}.]")
            return False

    def __draw(self, graph=None, position=None, directed=False, edge_labels={}):
        nx.draw_networkx_nodes(graph, position)
        nx.draw_networkx_edges(graph, position, arrows=directed)
        nx.draw_networkx_labels(graph, position)

        if edge_labels:
            nx.draw_networkx_edge_labels(graph, position, edge_labels=edge_labels)

    def __show(self):
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        plt.close()

    def export_highlight_path(self, path=list(), filename=None, save_to=os.getcwd()):
        pathGraph = nx.DiGraph()
        edges = list()
        edges_weighted = list()
        edge_labels = dict()
        highlight_edge_labels = dict()

        for i in range(0, len(path) - 1):
            edge = (path[i], path[i + 1])
            if self.weighted:
                edges_weighted.append((*edge, self.Graph.get_edge_data(*edge)['weight']))
                highlight_edge_labels.update(self.Graph.get_edge_data(*edge))
                highlight_edge_labels[edge] = highlight_edge_labels.pop('weight')
            edges.append(edge)

        # Temporary remove edges related to the path.
        self.Graph.remove_edges_from(edges)

        if self.weighted:
            edge_labels = nx.get_edge_attributes(self.Graph, 'weight')
        self.__draw(self.Graph, self.position, True, edge_labels)
        nx.draw_networkx_edges(pathGraph, self.position, edgelist=edges, edge_color="red", style="dashed")

        if edge_labels:
            nx.draw_networkx_edge_labels(pathGraph, self.position, edge_labels=highlight_edge_labels)

        directory = f"{save_to}\{filename}.png"
        if self.__save(directory):
            print(f"[Exported highlighted path to {directory}.]")
        else:
            print(f"[Failed to export highlighted path to {directory}.]")
        
        # Add back the removed edges.
        if self.weighted:
            self.Graph.add_weighted_edges_from(edges_weighted)
        else:
            self.Graph.add_edges_from(edges)

    def visualizeGraph(self):
        if self.Graph == None:
            print("[Please create the graph to visualize it.]")
            return
        self.__show()

    def visualizeTraverse(self, DFS=True):
        start_node = input("Start Node> ")
        if DFS:
            paths = self.__DFS(start_node=start_node)

            foldername = "DFS_result"
            if not os.path.exists(foldername):
                os.makedirs(foldername)
            for key, path in paths.items():
                filename = 'path_' + str(key)
                self.export_highlight_path(path, filename, foldername)
        else:
            traversal_tree, edge_labels = self.__BFS(start_node=start_node)

            pos = nx.spring_layout(traversal_tree, seed=15)
            self.__draw(traversal_tree, pos, True)
            nx.draw_networkx_edge_labels(traversal_tree, pos, edge_labels=edge_labels, font_color='red')
            
            self.__show()

    def visualSTF(self, all_paths=True):
        if self.Graph == None:
            print("[Please create the graph to find STF.]")
            return
        start_node = input("Start> ")
        
        if not all_paths:
            end_node = input("Target> ")
            if self.Graph.has_node(start_node) and self.Graph.has_node(end_node):
                path = nx.shortest_path(self.Graph, start_node, end_node)
                filename = f"{start_node}_to_{end_node}"
                self.export_highlight_path(path=path, filename=filename)
            else:
                print(f"[{start_node} -> {end_node} is unknown].")
        else:
            if self.Graph.has_node(start_node):
                paths = dict(nx.all_pairs_shortest_path(self.Graph))

                foldername = "Shortest_Paths"
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                for node in self.Graph.nodes():
                    if node != start_node and nx.has_path(self.Graph, start_node, node):
                        path = paths[start_node][node]
                        filename = f"{start_node}_to_{node}"
                        self.export_highlight_path(path=path, filename=filename, save_to=foldername)
            else:
                print(f"[{start_node} is unknown].")

def menu():
    print("\t\t\t+-------------VISUAL GRAPH OPERATIONS-------------+")
    print("\t\t\t|E. Exit Program.                                 |")
    print("\t\t\t|G. Graph status.                                 |")
    print("\t\t\t|GC. Change status.                               |")
    print("\t\t\t|S. Show graph.                                   |")
    print("\t\t\t|I. Adding edge(s).                               |")
    print("\t\t\t|R. Removing edge(s).                             |")
    print("\t\t\t|X. Shortest path(s).                             |")
    print("\t\t\t|A. Algorithms.                                   |")
    print("\t\t\t+-------------------------------------------------+>", end=' ')

def add_edge_operation():
    global VisualGraph
    print("\t\t\t+---------------ADDING---------------+")
    print("\t\t\t|0. Go back.                         |")
    print("\t\t\t|1. Add a single edge.               |")
    print("\t\t\t|2. Add edges from file.             |")
    print("\t\t\t+------------------------------------+>", end=' ')

    operation = input()
    
    os.system("cls")
    match(operation):
        case '0': return False
        case '1':
            valid_weight = True
            A = input("Vertice A> ")
            B = input("Vertice B> ")

            try:
                W = float(input(f"Weight of edge {A} {B}> "))
            except:
                valid_weight = False
            if len(A) == 0 or len(B) == 0 or valid_weight == False:
                print("[Invalid edge will be discarded.]")
            else:
                VisualGraph.addEdge(A, B, W)
        case '2':
            filename = input(".txt> ") + ".txt"
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        data = line
                        edge = data.strip().split(' ')
                        edge[2] = float(edge[2])
                        VisualGraph.addEdge(*edge)
                    f.close()
            except Exception as e:
                print(e)
        case _: print("[Invalid adding operation, re-enter.]")
    return True

def remove_edge_operation():
    global VisualGraph
    print("\t\t\t+--------------REMOVING--------------+")
    print("\t\t\t|0. Go back.                         |")
    print("\t\t\t|1. Remove a single edge.            |")
    print("\t\t\t|2. Remove all edges.                |")
    print("\t\t\t+------------------------------------+>", end=' ')

    operation = input()
    
    os.system("cls")
    match(operation):
        case '0': return False
        case '1':
            A = input("Vertice A> ")
            B = input("Vertice B> ")
            VisualGraph.removeEdge(A, B)
        case '2': VisualGraph.reset()
        case _: print("[Invalid removing operation, re-enter.]")
    return True

def visual_STF_operation():
    print("\t\t\t+-----------SHORTEST PATH------------+")
    print("\t\t\t|0. Go back.                         |")
    print("\t\t\t|1. From source to target            |")
    print("\t\t\t|2. From source to all vertices      |")
    print("\t\t\t+------------------------------------+>", end=' ')

    operation = input()
    
    os.system("cls")
    match(operation):
        case '0': return False
        case '1': VisualGraph.visualSTF(all_paths=False)
        case '2': VisualGraph.visualSTF(all_paths=True)
        case _: print("[Invalid shortest path operation, re-enter.]")
    return True

def algorithm_operations():
    print("\t\t\t+-------------ALGORITHMS-------------+")
    print("\t\t\t|0. Go back.                         |")
    print("\t\t\t|1. Depth first-search.              |")
    print("\t\t\t|2. Breath first-search.             |")
    print("\t\t\t|3. Dijkstra.                        |")
    print("\t\t\t|4. Bellman-Ford.                    |")
    print("\t\t\t+------------------------------------+>", end=' ')

    operation = input()

    os.system("cls")
    match(operation):
        case '0': return False
        case '1': VisualGraph.visualizeTraverse(DFS=True)
        case '2': VisualGraph.visualizeTraverse(DFS=False)
        case '3': VisualGraph.dijkstra()
        case '4': VisualGraph.bellman_ford()
        case _: print("[Invalid algorithm, re-enter.]")
    return True

def execute() -> bool():
    global VisualGraph
    menu()
    option = input().upper()

    os.system("cls")
    match(option):
        case 'E': return False
        case 'G': VisualGraph.status()
        case "GC": 
            if VisualGraph.Graph != None:
                print("[DIRECTED or WEIGHTED]")
                status_option = input("Choose status> ").upper()

                match(status_option):
                    case "DIRECTED":
                        previous_directed = VisualGraph.directed
                        if VisualGraph.directed == True:
                            VisualGraph.directed = False
                        else:
                            VisualGraph.directed = True
                        print(f"[Changed directed from {previous_directed} -> {VisualGraph.directed}.]")
                    case "WEIGHTED":
                        previous_weighted = VisualGraph.weighted
                        if VisualGraph.weighted == True:
                            VisualGraph.weighted = False
                        else:
                            VisualGraph.weighted = True
                        print(f"[Changed directed from {previous_weighted} -> {VisualGraph.weighted}.]")
                    case '_': print("[Invalid status option.]")
            else:
                print("[Graph does not exist.]")
        case 'S':
            VisualGraph.createGraph(directed=VisualGraph.directed, weighted=VisualGraph.weighted) 
            VisualGraph.visualizeGraph()
        case 'I':
            process = True
            while process:
                process = add_edge_operation()
        case 'R':
            process = True
            while process:
                process = remove_edge_operation()
        case 'X':
            VisualGraph.createGraph(directed=VisualGraph.directed, weighted=VisualGraph.weighted)
            process = True
            while process:
                process = visual_STF_operation()
        case 'A':
            VisualGraph.createGraph(directed=VisualGraph.directed, weighted=VisualGraph.weighted)
            process = True
            while process:
                process = algorithm_operations()
        case _: print("[Invalid option, re-enter.]")
    return True

def main() -> None:
    process = True
    while(process):
        process = execute()
    
    print("[End Program.]")


if __name__ == "__main__":
    VisualGraph = GraphVisualization()
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")