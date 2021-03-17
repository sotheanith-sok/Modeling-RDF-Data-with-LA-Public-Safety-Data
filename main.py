from Backend.rdf import RDF_Graph
rdf = RDF_Graph()


#https://data.lacity.org/resource/amvf-fr72
#https://data.lacity.org/resource/2nrs-mtv8

print(rdf.export("output.txt"))