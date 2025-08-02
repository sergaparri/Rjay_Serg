
def dfs_path(graph, start, goal, path=None, visited=None):
    if path is None: 
        path = []
    if visited is None: 
        visited = set()
    
    path.append(start)
    visited.add(start)
    
    if start == goal:
        return path
    
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result = dfs_path(graph, neighbor, goal, path.copy(), visited.copy())
            if result:
                return result
    
    return None 