import csv
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDFS, RDF, XSD

from contextlib import closing
import requests
import datetime

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

    def wtfman(self): 
        return 
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
        """Downalod dataset and decode them as csv

        Args:
            url (string): URL to download resources

        Returns:
            [string]: dataset formatted as csv
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
     
        for i in range(1, len(arrest_reports_dataset)): 
            number_report = len(list(graph.subject_objects(predicate=namespace["hasID"])))
            # add base arrest report that inherits from the report class
            graph.add((namespace["report" + str(number_report)], RDF.type, namespace["ArrestReport"]))
            graph.add((namespace["report" + str(number_report)], namespace["hasID"], Literal(arrest_reports_dataset[i][0], datatype=XSD.integer)))
            graph.add((namespace["report" + str(number_report)], namespace["hasDate"], Literal(arrest_reports_dataset[i][2], datatype=XSD.date)))
            graph.add((namespace["report" + str(number_report)], namespace["hasTime"], Literal(arrest_reports_dataset[i][3], datatype=XSD.time)))
            graph.add((namespace["report" + str(number_report)], namespace["hasReporType"], Literal(arrest_reports_dataset[i][1], datatype=XSD.string)))
            graph.add((namespace["report" + str(number_report)], namespace["hasArrestType"], Literal(arrest_reports_dataset[i][12], datatype=XSD.string)))
            graph.add((namespace["report" + str(number_report)], namespace["hasDispositionDescription"], Literal(arrest_reports_dataset[i][15], datatype=XSD.string)))

            # set up the people class
            people_age = set(graph.subjects(predicate = namespace["hasAge"], object=Literal(arrest_reports_dataset[i][7], datatype=XSD.integer)))
            people_sex = set(graph.subjects(predicate = namespace["hasSex"], object=Literal(arrest_reports_dataset[i][8], datatype=XSD.string)))
            people_decendent = set(graph.subjects(predicate = namespace["hasDescendent"], object=Literal(arrest_reports_dataset[i][9], datatype=XSD.string)))
            # returns the number of persons for the naming scheme
            number_person = len(list(graph.subject_objects(predicate=namespace["hasAge"])))
            # give all the triples with age, sex, and decendent
            person = list(people_age & people_sex & people_decendent)
            if(len(person) == 0): 
                # add to Person
                graph.add((namespace["Person" + str(number_person)], RDF.type, namespace["Person"]))
                graph.add((namespace["Person" + str(number_person)], namespace["hasAge"], Literal(arrest_reports_dataset[i][7], datatype=XSD.integer)))
                graph.add((namespace["Person" + str(number_person)], namespace["hasSex"], Literal(arrest_reports_dataset[i][8], datatype=XSD.string)))
                graph.add((namespace["Person" + str(number_person)], namespace["hasDescendent"], Literal(arrest_reports_dataset[i][9], datatype=XSD.string)))
                person = namespace["Person" + str(number_person)]
            else: 
                person = person[0]
            
            #setting up location
            number_location = len(list(graph.subject_objects(predicate=namespace["hasAreaID"])))
            location_reporting_dist = set(graph.subjects(predicate = namespace["hasReportingDistrictNumber"], object=Literal(arrest_reports_dataset[i][6], datatype=XSD.integer)))
            location_areaID = set(graph.subjects(predicate = namespace["hasAreaID"], object=Literal(arrest_reports_dataset[i][4], datatype=XSD.integer)))
            location_area_name = set(graph.subjects(predicate = namespace["hasAreaName"], object=Literal(arrest_reports_dataset[i][5], datatype=XSD.string)))
            location_address = set(graph.subjects(predicate = namespace["hasAddress"], object=Literal(arrest_reports_dataset[i][16], datatype=XSD.string)))
            location_cross_street = set(graph.subjects(predicate = namespace["hasCrossStreet"], object=Literal(arrest_reports_dataset[i][17], datatype=XSD.string)))
            location_lat = set(graph.subjects(predicate = namespace["hasLatitude"], object=Literal(arrest_reports_dataset[i][18], datatype=XSD.double)))
            location_lon = set(graph.subjects(predicate = namespace["hasLongtitude"], object=Literal(arrest_reports_dataset[i][19], datatype=XSD.double)))
            
            location = list(location_reporting_dist & location_areaID & location_area_name & location_address & location_cross_street & location_lat & location_lon)
            if(len(location) == 0): 
                # no location
                graph.add((namespace["Location" + str(number_location)], RDF.type, namespace["Location"]))
                graph.add((namespace["Location" + str(number_location)], namespace["hasReportingDistrictNumber"], Literal(arrest_reports_dataset[i][6], datatype=XSD.integer)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasAreaID"], Literal(arrest_reports_dataset[i][4], datatype=XSD.integer)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasAreaName"], Literal(arrest_reports_dataset[i][5], datatype=XSD.string)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasAddress"], Literal(arrest_reports_dataset[i][16], datatype=XSD.string)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasCrossStreet"], Literal(arrest_reports_dataset[i][17], datatype=XSD.string)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasLatitude"], Literal(arrest_reports_dataset[i][18], datatype=XSD.double)))
                graph.add((namespace["Location" + str(number_location)], namespace["hasLongtitude"], Literal(arrest_reports_dataset[i][19], datatype=XSD.double)))
                location = namespace["Location" + str(number_location)]
            else: 
                location = location[0]            

            # setting up booking
            number_booking = len(list(graph.subject_objects(predicate=namespace["hasBookingCode"])))
            booking_date = set(graph.subjects(predicate = namespace["hasBookingDate"], object=Literal(arrest_reports_dataset[i][21], datatype=XSD.date)))
            booking_time = set(graph.subjects(predicate = namespace["hasBookingTime"], object=Literal(arrest_reports_dataset[i][22], datatype=XSD.time)))
            booking_location = set(graph.subjects(predicate = namespace["hasBookingLocation"], object=Literal(arrest_reports_dataset[i][23], datatype=XSD.string)))
            booking_code = set(graph.subjects(predicate = namespace["hasBookingCode"], object=Literal(arrest_reports_dataset[i][24], datatype=XSD.integer)))

            booking = list(booking_date & booking_time & booking_location & booking_code)
            if(len(booking) == 0): 
                graph.add((namespace["Booking" + str(number_booking)], RDF.type, namespace["Booking"]))
                graph.add((namespace["Booking" + str(number_booking)], namespace["hasBookingDate"], Literal(arrest_reports_dataset[i][21], datatype=XSD.date)))
                graph.add((namespace["Booking" + str(number_booking)], namespace["hasBookingTime"], Literal(arrest_reports_dataset[i][22], datatype=XSD.time)))
                graph.add((namespace["Booking" + str(number_booking)], namespace["hasBookingLocation"], Literal(arrest_reports_dataset[i][23], datatype=XSD.string)))
                graph.add((namespace["Booking" + str(number_booking)], namespace["hasBookingCode"], Literal(arrest_reports_dataset[i][24], datatype=XSD.integer)))
                booking = namespace["Booking" + str(number_booking)]
            else: 
                booking = booking[0]
            
            # setting up charge
            number_charge = len(list(graph.subject_objects(predicate=namespace["hasChargeCode"])))
            charge_group_code = set(graph.subjects(predicate = namespace["hasChargeGroupCode"], object=Literal(arrest_reports_dataset[i][10], datatype=XSD.integer)))
            charge_group_description = set(graph.subjects(predicate = namespace["hasChargeGroupDescription"], object=Literal(arrest_reports_dataset[i][11], datatype=XSD.string)))
            charge_code = set(graph.subjects(predicate = namespace["hasChargeCode"], object=Literal(arrest_reports_dataset[i][13], datatype=XSD.integer)))
            charge_description = set(graph.subjects(predicate = namespace["hasChargeDescription"], object=Literal(arrest_reports_dataset[i][14], datatype=XSD.string)))

            charge = list(charge_group_code & charge_group_description & charge_code & charge_description)
            if(len(charge) == 0): 
                graph.add((namespace["Charge" + str(number_charge)], RDF.type, namespace["Charge"]))
                graph.add((namespace["Charge" +str(number_charge)], namespace["hasChargeGroupCode"], Literal(arrest_reports_dataset[i][10], datatype=XSD.integer)))
                graph.add((namespace["Charge" +str(number_charge)], namespace["hasChargeGroupDescription"], Literal(arrest_reports_dataset[i][11], datatype=XSD.string)))
                graph.add((namespace["Charge" +str(number_charge)], namespace["hasChargeCode"], Literal(arrest_reports_dataset[i][13], datatype=XSD.integer)))
                graph.add((namespace["Charge" +str(number_charge)], namespace["hasChargeDescription"], Literal(arrest_reports_dataset[i][14], datatype=XSD.string)))
                charge = namespace["Charge" + str(number_charge)]
            else: 
                charge = charge[0]

            #add to report
            graph.add((namespace["report" + str(number_report)], namespace["hasPerson"], person))
            graph.add((namespace["report" + str(number_report)], namespace["hasLocation"], location))
            graph.add((namespace["report" + str(number_report)], namespace["hasBooking"], booking))
            graph.add((namespace["report" + str(number_report)], namespace["hasCharge"], charge))
       
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
