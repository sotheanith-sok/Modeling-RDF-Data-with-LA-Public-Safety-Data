import csv
import rdflib
from contextlib import closing
import requests


class RDF:
    def __init__(self):
        """Initialize the RDF object

        Args:
            url (str, optional): [A location of JSON dataset]. Defaults to None.
        """

        # Initialize rdf graph
        self.graph = rdflib.Graph()

    def _validate_url(self, url):
        """Validate the URL to ensure that it is accessible. 

        Args:
            url (string): the URL to check

        Returns:
            boolean: true if the URL can be access else false
        """
        request = requests.get(url)
        if request.status_code == 200:
            return True
        else:
            print("Error: URL returns "+request.status_code)
            return False

    
    def _get_dataset(self, url):
        """Downalod dataset and decode them as json

        Args:
            url (string): URL to download resources

        Returns:
            string: dataset formatted as json
        """
        isAvailable = self._validate_url(url)

        if isAvailable:
            with closing(requests.get(url+".csv?$limit=999999999",stream=True)) as response:
                decoded_dataset = [line.decode('utf-8') for line in response.iter_lines()]
                dataset = csv.reader(decoded_dataset, delimiter=',')
                return list(dataset) 

    def _normalize_string(self, str):
        """Process and normalize data

        Args:
            str (str): string that need to be nomralize

        Returns:
            [str]: normalized string
        """

        str = ' '.join(str.split())

        return str
     

    def add(self, url):
        """Add dataset from url into RDF graph

        Args:
            url (str): destination of csv file of the dataset to be added to the RDF graph. 
        """
        dataset = self._get_dataset(url)

        base_url = url+"/"
        base_subject = url+".json?"+dataset[0][0]+"="
        predicates = dataset[0]

        for i in range(1,len(dataset)):
            subject = rdflib.URIRef(base_subject + dataset[i][0])
            namespace = rdflib.Namespace(base_url)
            for j in range(len(predicates)):
                predicate = namespace[predicates[j]]
                obj = rdflib.Literal(self._normalize_string(dataset[i][j]))
                self.graph.add((subject,predicate,obj))
                
    def export(self, destination=None, format="pretty-xml"):
        """Export RDF graph as a string or a file. Set destination to export as a file

        Args:
            destination (str, optional): specific location and filename to save the RDF export file to. Default to None.
            format (str, optional): format of the export RDF graph. Defaults to "xml".

        Returns:
            [output]: [return the seralized result of RDF graph]
        """

        if destination:
            self.graph.serialize(destination=destination,format=format)
        else:
            return self.graph.serialize(format=format).decode("utf-8")

