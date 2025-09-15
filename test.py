# Python3 program to construct 
# tree from given Prufer Code 

# Prints edges of tree represented
# by given Prufer code 
def printTreeEdges(prufer, m):
	
	vertices = m + 2
	
	# Initialize the array of vertices 
	vertex_set = [0] * vertices
	
	# Number of occurrences of vertex in code 
	for i in range(vertices - 2):
		vertex_set[prufer[i] - 1] += 1
	
	print("The edge set E(G) is :")
	
	# Find the smallest label not present in 
	# prufer. 
	j = 0
	for i in range(vertices - 2):
		for j in range(vertices):
			
			# If j+1 is not present in prufer set 
			if (vertex_set[j] == 0):
				
				# Remove from Prufer set and print 
				# pair. 
				vertex_set[j] = -1
				print("(" , (j + 1),", ",prufer[i],") ",sep = "",end = "")
				vertex_set[prufer[i] - 1] -= 1
				break
	
	j = 0
	
	# For the last element 
	for i in range(vertices):
		if (vertex_set[i] == 0 and j == 0):
			print("(", (i + 1),", ", sep="", end="")
			j += 1
		elif (vertex_set[i] == 0 and j == 1):
			print((i + 1),")")

# Driver code 
prufer = [4,4,4,7,1,9,1]
n = len(prufer) 
printTreeEdges(prufer, n) 

# This code is contributed by SHUBHAMSINGH10
