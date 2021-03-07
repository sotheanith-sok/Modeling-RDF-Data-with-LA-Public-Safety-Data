from Backend.rdf import RDF
rdf = RDF("https://data.lacity.org/resource/amvf-fr72.json")
rdf.build_graph()