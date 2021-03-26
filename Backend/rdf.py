import csv
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDFS, RDF, XSD
import pandas as pd

from contextlib import closing
import requests


class RDF_Graph:
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

        #Defines 'Report' class and its associated proprties
        graph.add((namespace['Report'], RDF.type, RDFS.Class))

        graph.add((namespace['hasID'], RDF.type, RDF.Property))
        graph.add((namespace['hasPerson'], RDF.type, RDF.Property))
        graph.add((namespace['hasTime'], RDF.type, RDF.Property))
        graph.add((namespace['hasDate'], RDF.type, RDF.Property))
        graph.add((namespace['hasLocation'], RDF.type, RDF.Property))

        graph.add((namespace['hasID'], RDFS.domain, namespace['Report']))
        graph.add((namespace['hasPerson'], RDFS.domain, namespace['Report']))
        graph.add((namespace['hasTime'], RDFS.domain, namespace['Report']))
        graph.add((namespace['hasDate'], RDFS.domain, namespace['Report']))
        graph.add((namespace['hasLocation'], RDFS.domain, namespace['Report']))

        graph.add((namespace['hasID'], RDFS.range, XSD.integer))
        graph.add((namespace['hasPerson'], RDFS.range, namespace['Person']))
        graph.add((namespace['hasTime'], RDFS.range, XSD.time))
        graph.add((namespace['hasDate'], RDFS.range, XSD.date))
        graph.add((namespace['hasLocation'], RDFS.range, namespace['Location']))

        #Define 'Person' class and its associated properties
        graph.add((namespace['Person'],RDF.type, RDFS.Class))

        graph.add((namespace['hasAge'], RDF.type, RDF.Property))
        graph.add((namespace['hasSex'], RDF.type, RDF.Property))
        graph.add((namespace['hasDescendent'], RDF.type, RDF.Property))

        graph.add((namespace['hasAge'],RDFS.domain, namespace['Person']))
        graph.add((namespace['hasSex'],RDFS.domain, namespace['Person']))
        graph.add((namespace['hasDescendent'],RDFS.domain, namespace['Person']))

        graph.add((namespace['hasAge'],RDFS.range, XSD.integer))
        graph.add((namespace['hasSex'],RDFS.range,XSD.string))
        graph.add((namespace['hasDescendent'],RDFS.range, XSD.string))

        #Define 'Location' class and its associated properties
        graph.add((namespace['Location'],RDF.type, RDFS.Class))

        graph.add((namespace['hasReportingDistrictNumber'], RDF.type, RDF.Property))
        graph.add((namespace['hasAreaID'], RDF.type, RDF.Property))
        graph.add((namespace['hasAreaName'], RDF.type, RDF.Property))
        graph.add((namespace['hasAddress'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrossStreet'], RDF.type, RDF.Property))
        graph.add((namespace['hasLatitude'], RDF.type, RDF.Property))
        graph.add((namespace['hasLongtitude'], RDF.type, RDF.Property))
        
        graph.add((namespace['hasReportingDistrictNumber'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasAreaID'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasAreaName'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasAddress'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasCrossStreet'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasLatitude'], RDFS.domain, namespace['Location']))
        graph.add((namespace['hasLongtitude'], RDFS.domain, namespace['Location']))

        graph.add((namespace['hasReportingDistrictNumber'], RDFS.range, XSD.integer))
        graph.add((namespace['hasAreaID'], RDFS.range, XSD.integer))
        graph.add((namespace['hasAreaName'], RDFS.range, XSD.string))
        graph.add((namespace['hasAddress'], RDFS.range, XSD.string))
        graph.add((namespace['hasCrossStreet'], RDFS.range, XSD.string))
        graph.add((namespace['hasLatitude'], RDFS.range, XSD.double))
        graph.add((namespace['hasLongtitude'], RDFS.range, XSD.double))

        #Define "ArrestReport" class and its associated properties
        graph.add((namespace['ArrestReport'], RDFS.subClassOf, namespace['Report']))

        graph.add((namespace['hasCharge'], RDF.type, RDF.Property))
        graph.add((namespace['hasBooking'], RDF.type, RDF.Property))
        graph.add((namespace['hasDispositionDescription'], RDF.type, RDF.Property))
        graph.add((namespace['hasReporType'], RDF.type, RDF.Property))
        graph.add((namespace['hasArrestType'], RDF.type, RDF.Property))

        graph.add((namespace['hasCharge'], RDFS.domain, namespace['ArrestReport']))
        graph.add((namespace['hasBooking'], RDFS.domain, namespace['ArrestReport']))
        graph.add((namespace['hasDispositionDescription'], RDFS.domain, namespace['ArrestReport']))
        graph.add((namespace['hasReporType'], RDFS.domain, namespace['ArrestReport']))
        graph.add((namespace['hasArrestType'], RDFS.domain, namespace['ArrestReport']))

        graph.add((namespace['hasCharge'], RDFS.range, namespace['Charge']))
        graph.add((namespace['hasBooking'], RDFS.range, namespace['Booking']))
        graph.add((namespace['hasDispositionDescription'], RDFS.range, XSD.string))
        graph.add((namespace['hasReporType'], RDFS.range, XSD.string))
        graph.add((namespace['hasArrestType'], RDFS.range, XSD.string))

        #Define "Charge" class and its associated properties
        graph.add((namespace['Charge'],RDF.type, RDFS.Class))

        graph.add((namespace['hasChargeGroupCode'], RDF.type, RDF.Property))
        graph.add((namespace['hasChargeGroupDescription'], RDF.type, RDF.Property))
        graph.add((namespace['hasChargeCode'], RDF.type, RDF.Property))
        graph.add((namespace['hasChargeDescription'], RDF.type, RDF.Property))

        graph.add((namespace['hasChargeGroupCode'], RDFS.domain, namespace['Charge']))
        graph.add((namespace['hasChargeGroupDescription'], RDFS.domain, namespace['Charge']))
        graph.add((namespace['hasChargeCode'], RDFS.domain, namespace['Charge']))
        graph.add((namespace['hasChargeDescription'], RDFS.domain, namespace['Charge']))

        graph.add((namespace['hasChargeGroupCode'], RDFS.range, XSD.integer))
        graph.add((namespace['hasChargeGroupDescription'], RDFS.range, XSD.string))
        graph.add((namespace['hasChargeCode'], RDFS.range, XSD.string))
        graph.add((namespace['hasChargeDescription'], RDFS.range, XSD.string))

        #Define "Booking" class and its associated properties
        graph.add((namespace['Booking'],RDF.type, RDFS.Class))

        graph.add((namespace['hasBookingDate'], RDF.type, RDF.Property))
        graph.add((namespace['hasBookingTime'], RDF.type, RDF.Property))
        graph.add((namespace['hasBookingLocation'], RDF.type, RDF.Property))
        graph.add((namespace['hasBookingCode'], RDF.type, RDF.Property))

        graph.add((namespace['hasBookingDate'], RDFS.domain, namespace['Booking']))
        graph.add((namespace['hasBookingTime'], RDFS.domain, namespace['Booking']))
        graph.add((namespace['hasBookingLocation'], RDFS.domain, namespace['Booking']))
        graph.add((namespace['hasBookingCode'], RDFS.domain, namespace['Booking']))

        graph.add((namespace['hasBookingDate'], RDFS.range, XSD.date))
        graph.add((namespace['hasBookingTime'], RDFS.range, XSD.time))
        graph.add((namespace['hasBookingLocation'], RDFS.range, XSD.string))
        graph.add((namespace['hasBookingCode'], RDFS.range, XSD.integer))

        #Define "CrimeReport" class and its associated properties
        graph.add((namespace['CrimeReport'], RDFS.subClassOf, namespace['Report']))

        graph.add((namespace['hasDateReported'], RDF.type, RDF.Property))
        graph.add((namespace['hasMocodes'], RDF.type, RDF.Property))
        graph.add((namespace['hasPart1-2'], RDF.type, RDF.Property))
        graph.add((namespace['hasPremise'], RDF.type, RDF.Property))
        graph.add((namespace['hasWeapon'], RDF.type, RDF.Property))
        graph.add((namespace['hasStatus'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrime'], RDF.type, RDF.Property))

        graph.add((namespace['hasDateReported'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasMocodes'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasPart1-2'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasPremise'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasWeapon'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasStatus'], RDFS.domain, namespace['CrimeReport']))
        graph.add((namespace['hasCrime'], RDFS.domain, namespace['CrimeReport']))

        graph.add((namespace['hasDateReported'], RDFS.range, XSD.date))
        graph.add((namespace['hasMocodes'], RDFS.range, XSD.integer))
        graph.add((namespace['hasPart1-2'], RDFS.range, XSD.integer))
        graph.add((namespace['hasPremise'], RDFS.range, namespace['Premise']))
        graph.add((namespace['hasWeapon'], RDFS.range, namespace['Weapon']))
        graph.add((namespace['hasStatus'], RDFS.range, namespace['Status']))
        graph.add((namespace['hasCrime'], RDFS.range, namespace['Crime']))

        #Define "Crime" class and its property
        graph.add((namespace['Crime'],RDF.type, RDFS.Class))

        graph.add((namespace['hasCrimeCommittedDescription'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrimeCommitted'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrimeCommitted1'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrimeCommitted2'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrimeCommitted3'], RDF.type, RDF.Property))
        graph.add((namespace['hasCrimeCommitted4'], RDF.type, RDF.Property))

        graph.add((namespace['hasCrimeCommittedDescription'], RDFS.domain, namespace['Crime']))
        graph.add((namespace['hasCrimeCommitted'], RDFS.domain, namespace['Crime']))
        graph.add((namespace['hasCrimeCommitted1'], RDFS.domain, namespace['Crime']))
        graph.add((namespace['hasCrimeCommitted2'], RDFS.domain, namespace['Crime']))
        graph.add((namespace['hasCrimeCommitted3'], RDFS.domain, namespace['Crime']))
        graph.add((namespace['hasCrimeCommitted4'], RDFS.domain, namespace['Crime']))

        graph.add((namespace['hasCrimeCommittedDescription'], RDFS.range, XSD.string))
        graph.add((namespace['hasCrimeCommitted'], RDFS.range, XSD.integer))
        graph.add((namespace['hasCrimeCommitted1'], RDFS.range, XSD.integer))
        graph.add((namespace['hasCrimeCommitted2'], RDFS.range, XSD.integer))
        graph.add((namespace['hasCrimeCommitted3'], RDFS.range, XSD.integer))
        graph.add((namespace['hasCrimeCommitted4'], RDFS.range, XSD.integer))

        #Define 'Premise' class and its properties
        graph.add((namespace['Premise'],RDF.type, RDFS.Class))

        graph.add((namespace['hasPremiseCode'], RDF.type, RDF.Property))
        graph.add((namespace['hasPremiseDescription'], RDF.type, RDF.Property))

        graph.add((namespace['hasPremiseCode'], RDFS.domain, namespace['Premise']))
        graph.add((namespace['hasPremiseDescription'], RDFS.domain, namespace['Premise']))

        graph.add((namespace['hasPremiseCode'], RDFS.range, XSD.integer))
        graph.add((namespace['hasPremiseDescription'], RDFS.range, XSD.string))

        #Define 'Weapon' class and its properties
        graph.add((namespace['Weapon'],RDF.type, RDFS.Class))

        graph.add((namespace['hasWeaponUsedCode'], RDF.type, RDF.Property))
        graph.add((namespace['hasWeaponDescription'], RDF.type, RDF.Property))

        graph.add((namespace['hasWeaponUsedCode'], RDFS.domain, namespace['Weapon']))
        graph.add((namespace['hasWeaponDescription'], RDFS.domain, namespace['Weapon']))

        graph.add((namespace['hasWeaponUsedCode'], RDFS.range, XSD.integer))
        graph.add((namespace['hasWeaponDescription'], RDFS.range, XSD.string))

        #Define 'Status' class and its properties
        graph.add((namespace['Status'],RDF.type, RDFS.Class))

        graph.add((namespace['hasStatusCode'], RDF.type, RDF.Property))
        graph.add((namespace['hasStatusDescription'], RDF.type, RDF.Property))

        graph.add((namespace['hasStatusCode'], RDFS.domain, namespace['Status']))
        graph.add((namespace['hasStatusDescription'], RDFS.domain, namespace['Status']))

        graph.add((namespace['hasStatusCode'], RDFS.range, XSD.integer))
        graph.add((namespace['hasStatusDescription'], RDFS.range, XSD.string))
        
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

        colNames = ['ReportID', 'DataReported', 'DateOCC', 'TimeOCC', 'Area',
            'AreaName', 'ReportDistrict', 'Part-1-2', 'CrimeCommited',
            'CrimeDescription', 'Mocodes', 'Age', 'SexCode',
            'DescendentCode', 'PremiseCode', 'PremiseDescription',
            'WeaponCode', 'WeaponDescription', 'Status',
            'StatusDescription', 'CrimCommited1', 'CrimCommited2',
            'CrimCommited3', 'CrimCommited4', 'location',
            'CrossStreet', 'lat', 'lon']
        df = pd.DataFrame (crime_reports_dataset[1:], columns=colNames)
        dr_no_list = df['ReportID']

        # Person
        age_list = df['Age']
        sex_list = df['SexCode']
        descendent_list = df['DescendentCode']

        # Time Occured
        time_list = df['TimeOCC']

        # Date Occured
        date_list = df['DateOCC']

        # Location
        reportDist = df['ReportDistrict']
        areaList = df['Area']
        areaNameList = df['AreaName']
        locationList = df['location']
        crossStreetList = df['CrossStreet']
        latList = df['lat']
        lonList = df['lon']

        # Date Reported
        mocodesList = df['Mocodes']

        # Date Reported
        date_reported = df['DataReported']

        # Part 1-2
        part_1_2 = df['Part-1-2']

        # Premise
        premiseCodeList = df['PremiseCode']
        premiseDescriptionList = df['PremiseDescription']

        # Weapon
        weaponUsedList = df['WeaponCode']
        weaponDescriptionList = df['WeaponDescription']

        # Status
        statusList = df['Status']
        statusDescriptionList = df['StatusDescription']

        # Crimes
        CrimCommitedList = df['CrimeCommited']
        CrimeDescriptionList = df['CrimeDescription']
        CrimCommited1List = df['CrimCommited1']
        CrimCommited2List = df['CrimCommited2']
        CrimCommited3List = df['CrimCommited3']
        CrimCommited4List = df['CrimCommited4']

        """Report ID

        """

        for index, value in dr_no_list.items():
            graph.add((namespace["Report" + str(index)], RDF.type, namespace["CrimeReport"]))
            graph.add((namespace["Report" + str(index)], namespace["hasID"], Literal(value, datatype=XSD.integer)))

        """Person"""

        for index, value in age_list.items():
            # graph.add((namespace["Person" + str(index)], RDF.type, namespace["Person"]))
            graph.add((namespace["Person" + str(index)], namespace["hasAge"], Literal(value, datatype=XSD.integer)))
            person = namespace["Person" + str(index)]
            graph.add((namespace["Report" + str(index)], namespace["hasPerson"], person))

        for index, value in sex_list.items():
            # graph.add((namespace["Person" + str(index)], RDF.type, namespace["Person"]))
            graph.add((namespace["Person" + str(index)], namespace["hasSex"], Literal(value, datatype=XSD.string)))
            person = namespace["Person" + str(index)]
            graph.add((namespace["Report" + str(index)], namespace["hasPerson"], person))

        for index, value in descendent_list.items():
            # graph.add((namespace["Person" + str(index)], RDF.type, namespace["Person"]))
            graph.add((namespace["Person" + str(index)], namespace["hasDescendent"], Literal(value, datatype=XSD.string)))
            person = namespace["Person" + str(index)]
            graph.add((namespace["Report" + str(index)], namespace["hasPerson"], person))

        """Time OCC"""

        for index, value in time_list.items():
            graph.add((namespace["Report" + str(index)], namespace["hasTime"], Literal(value, datatype=XSD.time)))

        """Date OCC"""

        for index, value in date_list.items():
            graph.add((namespace["Report" + str(index)], namespace["hasDate"], Literal(value, datatype=XSD.date)))

        """Location"""

        for index, value in reportDist.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasReportingDisctrictNumber"],
                Literal(value, datatype=XSD.integer)))

        for index, value in areaList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasAreaID"], Literal(value, datatype=XSD.integer)))

        for index, value in areaNameList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasAreaName"], Literal(value, datatype=XSD.string)))

        for index, value in locationList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasAddress"], Literal(value, datatype=XSD.string)))

        for index, value in crossStreetList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasCrossStreet"], Literal(value, datatype=XSD.string)))

        for index, value in latList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasLatitude"], Literal(value, datatype=XSD.double)))

        for index, value in lonList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasLocation"], namespace["Location" + str(index)]))
            # graph.add((namespace["Location" + str(index)], RDF.type, namespace["Location"]))
            graph.add((namespace["Location" + str(index)], namespace["hasLongitude"], Literal(value, datatype=XSD.double)))

        """# Subclass
        Date reported
        """

        for index, value in date_reported.items():
            graph.add((namespace["Report" + str(index)], namespace["hasDateReported"], Literal(value, datatype=XSD.date)))

        """Mocodes"""

        for index, value in mocodesList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasMocodes"], Literal(value, datatype=XSD.string)))

        """Part 1-2"""

        for index, value in part_1_2.items():
            graph.add((namespace["Report" + str(index)], namespace["hasPart1-2"], Literal(value, datatype=XSD.integer)))

        """Premise"""

        for index, value in premiseCodeList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasPremise"], namespace["Premise" + str(index)]))
            graph.add((namespace["Premise" + str(index)], RDF.type, namespace["Premise"]))
            graph.add((namespace["Premise" + str(index)], namespace["hasPremiseCode"], Literal(value, datatype=XSD.integer)))

        for index, value in premiseDescriptionList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasPremise"], namespace["Premise" + str(index)]))
            graph.add((namespace["Premise" + str(index)], RDF.type, namespace["Premise"]))
            graph.add((namespace["Premise" + str(index)], namespace["hasPremiseDescription"], Literal(value, datatype=XSD.string)))

        """Weapon

        """

        for index, value in weaponUsedList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasWeapon"], namespace["Weapon" + str(index)]))
            graph.add((namespace["Weapon" + str(index)], RDF.type, namespace["Weapon"]))
            graph.add((namespace["Weapon" + str(index)], namespace["hasWeaponCode"], Literal(value, datatype=XSD.integer)))

        for index, value in weaponDescriptionList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasWeapon"], namespace["Weapon" + str(index)]))
            graph.add((namespace["Weapon" + str(index)], RDF.type, namespace["Weapon"]))
            graph.add((namespace["Weapon" + str(index)], namespace["hasWeaponDescription"], Literal(value, datatype=XSD.string)))

        """Status"""

        for index, value in statusList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasStatus"], namespace["Status" + str(index)]))
            graph.add((namespace["Status" + str(index)], RDF.type, namespace["Status"]))
            graph.add((namespace["Status" + str(index)], namespace["hasStatusCode"], Literal(value, datatype=XSD.string)))

        for index, value in weaponDescriptionList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasStatus"], namespace["Status" + str(index)]))
            graph.add((namespace["Status" + str(index)], RDF.type, namespace["Status"]))
            graph.add((namespace["Status" + str(index)], namespace["hasStatusDescription"], Literal(value, datatype=XSD.string)))

        """Crimes"""

        for index, value in CrimCommitedList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCommitted"], Literal(value, datatype=XSD.integer)))

        for index, value in CrimeDescriptionList.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCrimmitedDescription"],
                Literal(value, datatype=XSD.string)))

        for index, value in CrimCommited1List.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCommited1"], Literal(value, datatype=XSD.integer)))

        for index, value in CrimCommited2List.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCommited2"], Literal(value, datatype=XSD.integer)))

        for index, value in CrimCommited3List.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCommited3"], Literal(value, datatype=XSD.string)))

        for index, value in CrimCommited4List.items():
            graph.add((namespace["Report" + str(index)], namespace["hasCrime"], namespace["Crime" + str(index)]))
            graph.add((namespace["Crime" + str(index)], RDF.type, namespace["Crime"]))
            graph.add((namespace["Crime" + str(index)], namespace["hasCrimeCommited4"], Literal(value, datatype=XSD.string)))
        return graph

