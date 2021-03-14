import csv
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from contextlib import closing
import requests


class RDF:
    def __init__(self, base_url = "https://data.lacity.org/",  arrest_reports_url ="https://data.lacity.org/resource/amvf-fr72", crime_reports_url = "https://data.lacity.org/resource/2nrs-mtv8" ):

        # Initalize URL
        self.base_url=base_url
        self.arrest_reports_url = arrest_reports_url
        self.crime_reports_url = crime_reports_url
        
        # Initialize rdf graph and namespace
        self.graph = Graph()
        self.namespace = Namespace(base_url)

        #Get datasets
        self.arrest_reports_dataset = self._get_dataset(self.arrest_reports_url)
        self.crime_reports_dataset = self._get_dataset(self.crime_reports_url)

        #Add base structure to the graph
        self.graph = self._add_base_structures_to_graph(self.graph,self.namespace)

        #Process and add arrest reports dataset to the graph
        self.arrest_reports_dataset = self._processing_arrest_reports_dataset(self.arrest_reports_dataset)
        self.graph = self._add_arrest_reports_dataset_to_graph(self.arrest_reports_dataset, self.graph,self.namespace)

        #Process and add crime reports dataset to the graph
        self.crime_reports_dataset = self._processing_crime_reports_dataset(self.crime_reports_dataset)
        self.graph = self._add_crime_reports_dataset_to_graph(self.crime_reports_dataset, self.graph,self.namespace)


    def _validate_url(self, url):
        """Validate the URL to ensure that it is accessible. 

        Args:
            url (string): the URL to check

        Returns:
            boolean: true if the URL can be access else false
        """
        print("INFO: Validating \""+url+"\"...")
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
            [string]: dataset formatted as json
        """
        isAvailable = self._validate_url(url)

        if isAvailable:
            print("INFO: Downloading dataset from \""+url+"\"...")
            with closing(requests.get(url+".csv?$limit=99999999",stream=True)) as response:
                decoded_dataset = [line.decode('utf-8') for line in response.iter_lines()]
                dataset = csv.reader(decoded_dataset, delimiter=',')
                return list(dataset) 
                
    def export(self, destination=None, format="pretty-xml"):
        """Export RDF graph as a string or a file. Set destination to export as a file

        Args:
            destination (str, optional): specific location and filename to save the RDF export file to. Default to None.
            format (str, optional): format of the export RDF graph. Defaults to "xml". Can also be CSV

        Returns:
            [output]: The seralized result of RDF graph
        """

        if format=="csv":
            if destination:

                #Filepaths building
                paths= destination.split('.')

                filename = paths[len(paths)-2]

                paths[len(paths)-2]=filename+"_arrest_reports"
                arrest_reports_filepath = '.'.join(paths)

                paths[len(paths)-2]=filename+"_crime_reports"
                crime_reports_filepath = '.'.join(paths)

                #Write CSV to files
                with open(arrest_reports_filepath, "wt") as fp:
                    writer = csv.writer(fp,delimiter=",")
                    writer.writerows(self.arrest_reports_dataset)

                with open(crime_reports_filepath, "wt") as fp:
                    writer = csv.writer(fp,delimiter=",")
                    writer.writerows(self.crime_reports_dataset)
            else:
                return self.arrest_reports_dataset, self.crime_reports_dataset
        else:
            if destination:
                self.graph.serialize(destination=destination,format=format)
            else:
                return self.graph.serialize(format=format).decode("utf-8")

    
    def _add_base_structures_to_graph(self,graph, namespace):
        """Add base structure to an RDF graph

        Args:
            graph (Graph): an RDF graph
            namespace (string): base namespace for all resources

        Returns:
            [Graph]: an RDF graph contains RDF base structure 
        """
        print("INFO: Add base structure to graph...")

        
        return graph


    def _processing_arrest_reports_dataset(self, arrest_reports_dataset):
        """Process all data in arrest reports such that all datapoints match formal specifications

        Args:
            arrest_reports_dataset (string): a CSV contains arrest reports

        Returns:
            [string]: a CSV contains arrest reports with well-formatted datapoints
        """
        print("INFO: Processing arrest reports dataset...")
        
        return arrest_reports_dataset


    def _add_arrest_reports_dataset_to_graph(self, arrest_reports_dataset, graph, namespace):
        """Add arrest reports dataset to the RDF graph

        Args:
            arrest_reports_dataset (string): a CSV contains arrest reports with well-formatted datapoints
            graph (Graph): an RDF graph
            namespace (string): base namespace for all resources

        Returns:
            [Graph]: an RDF graph contains data from the arrest report dataset
        """
        print("INFO: Add arrests dataset to graph...")

        return graph


    def _processing_crime_reports_dataset(self, crime_reports_dataset):
        """Process all data in crime reports such that all datapoints match formal specifications

        Args:
            crime_reports_dataset (string): a CSV contains crime reports

        Returns:
            [string]: a CSV contains crime reports with well-formatted datapoints
        """
        print("INFO: Processing crime reports dataset...")
        
        return crime_reports_dataset


    def _add_crime_reports_dataset_to_graph(self, crime_reports_dataset, graph, namespace):
        """Add crime reports dataset to the RDF graph

        Args:
            crime_reports_dataset (string): a CSV contains crime reports with well-formatted datapoints
            graph (Graph): an RDF graph
            namespace (string): base namespace for all resources

        Returns:
            [Graph]: an RDF graph contains data from the crime report dataset
        """
        print("INFO: Add crime reports dataset to graph...")

        return graph

