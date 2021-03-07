import urllib.request
import json
import rdflib


class RDF:
    def __init__(self, url=None):
        """Initialize the RDF object

        Args:
            url (str, optional): [A location of JSON dataset]. Defaults to None.
        """

        #Save the url
        self.url = url

        #Curl api and download all json data
        with urllib.request.urlopen(url+"?$limit=99999999") as url:
            self.dataset = json.loads(url.read())

        #Initialize rdf graph
        self.graph = rdflib.Graph()

    def build_graph(self):
        for i in range(len(self.dataset)):
            ID0 = self.dataset[i]["rpt_id"]

            with urllib.request.urlopen(self.url+"?rpt_id="+self.dataset[i]["rpt_id"]) as url:
                ID1=json.loads(url.read())[0]["rpt_id"]

            print(ID0 + ":" +ID1)

        pass

    def export(self, format="xml"):
        """Export RDF graph to a certain format

        Args:
            format (str, optional): [description]. Defaults to "xml".

        Returns:
            [output]: [return the seralized result of RDF graph]
        """
        return self.graph.serialize(format=format).decode("utf-8")
