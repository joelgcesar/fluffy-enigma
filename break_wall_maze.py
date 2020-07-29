moves=((-1,0),(0,-1),(0,1),(1,0))
arbitrary_large_value = 500

class Node():
    
    """ This class holds position and distance/step from origin"""
    
    def __init__(self,step=None,position=None):
        self.step=step              #
        self.pos=position
        
    def __eq__(self, other):
        return(self.pos==other.pos) #this helps to access nodes in lists

def base_maze_solve(maze_map, start, boardheight, boardwidth):
    
    """Function takes in maze map, dimensions, and starting point
        and returns a list of nodes."""
        
    step=1
    start_node=Node(step,start)     #creates starting node
    
    open_nodes = []                 #list of nodes being looked at
    closed_nodes = []               #list of nodes with final values to be returned
    open_nodes.append(start_node)   #adds starting node to open_nodes
    
    ## This loop creates a node with a distance from the start for every reachable
    ## floor tile. 
    
    while(len(open_nodes)>0):
        step=step+1
        next_nodes=[]
        for node in open_nodes:
            for pos in moves:
                new_pos = node.pos[0]+pos[0],node.pos[1]+pos[1]
                if (0<=new_pos[0]<boardheight)&(0<=new_pos[1]<boardwidth):
                    if (maze_map[new_pos[0]][new_pos[1]]==0):
                        new_node=Node(step,new_pos)
                        if ((new_node in next_nodes) or (new_node in closed_nodes)):
                            continue
                        else:
                            next_nodes.append(new_node)
            closed_nodes.append(node)
        open_nodes = [node for node in next_nodes]
    return(closed_nodes)
    
def break_wall_maze(maze_map):
    boardwidth=len(maze_map[0])                     #width of the maze
    boardheight=len(maze_map)                       #height of the maze
    start,end=(0,0),(boardheight-1,boardwidth-1)    #start and end points
    
    ## The base_maze_solve function gets called twice.
    ## Once starting from the start, and once starting from the end.
    
    distance_from_start = base_maze_solve(maze_map,start,boardheight, boardwidth)
    distance_from_end = base_maze_solve(maze_map, end, boardheight, boardwidth)
    
    ## This list comprehension creates a node for every wall tile -> value: 1
    
    wall_nodes=[Node(0, (i,j)) for i in range(boardheight) for j in range(boardwidth) if maze_map[i][j]==1]
    step_minimum = arbitrary_large_value
    
    ## For every wall node, we find the minimum values of distance_from_start
    ## and distance_from_end for the nodes surrounding the wall node.
    
    for node in wall_nodes:
        from_start=[arbitrary_large_value]
        from_end=[arbitrary_large_value]
        for pos in moves:
            new_pos = node.pos[0]+pos[0],node.pos[1]+pos[1]
            if (0<=new_pos[0]<boardheight)&(0<=new_pos[1]<boardwidth):
                if (maze_map[new_pos[0]][new_pos[1]]==0):
                    new_node=Node(0, new_pos)
                    if new_node in distance_from_start:
                        from_start.append(distance_from_start[distance_from_start.index(new_node)].step)
                    if new_node in distance_from_end:
                        from_end.append(distance_from_end[distance_from_end.index(new_node)].step)
        
        ## the sums of the minimums of these values plus one computes the 
        ## minimum maze distance going through that wall node. The absolute
        ## minimum across all wall nodes is the shortest solution to the maze.
        
        if(min(from_start)+min(from_end)+1<step_minimum):
            step_minimum=min(from_start)+min(from_end)+1
    
    return(step_minimum)
