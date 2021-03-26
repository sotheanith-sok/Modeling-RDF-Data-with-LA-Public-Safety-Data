import csv
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDFS, RDF, XSD
import pandas as pd

from contextlib import closing
import requests

class RDF_Graph:
    def __init__(self, base_url = "https://data.lacity.org/",  arrest_reports_url ="https://data.lacity.org/resource/amvf-fr72", crime_reports_url = "https://data.lacity.org/resource/2nrs-mtv8", max_data_count = 1000 ):
        # Initalize URL
        self.base_url=base_url
        self.arrest_reports_url = arrest_reports_url
        self.crime_reports_url = crime_reports_url

        # Initialize rdf graph and namespace
        self.graph = Graph()
        self.namespace = Namespace(base_url)

        #Get datasets
        self.arrest_reports_dataset = self._get_dataset(self.arrest_reports_url, max_data_count)
        self.crime_reports_dataset = self._get_dataset(self.crime_reports_url, max_data_count)

        #Add arrest reports dataset to the graph
        self.graph = self._add_arrest_reports_to_graph(self.arrest_reports_dataset, self.graph,self.namespace)

        #Add crime reports dataset to the graph
        self.graph = self._add_crime_reports_to_graph(self.crime_reports_dataset, self.graph,self.namespace)

  
    def _validate_url(self, url):
        """Validate the URL to ensure that it is accessible. 

        Args:
            url (string): the URL to check

        Returns:
            boolean: True if the URL can be accessed else False
        """

        #Print out the process
        print("INFO: Validating \"%s\"..." % url)

        #Make a GET request
        request = requests.get(url)

        #Check respond from the Get request
        if request.status_code == 200:
            return True
        else:
            print("Error: URL returns "+request.status_code)
            return False

    
    def _get_dataset(self, url, max_data_count):
        """Downalod dataset and decode them as csv

        Args:
            url (string): URL to download dataset
            max_data_count (int): maximum number of data to download for a given dataset

        Returns:
            [string]: List of data formatted as CSV
        """

        #Check if url is available
        isAvailable = self._validate_url(url)

        #If url is available
        if isAvailable:

            #Check how many data are available
            available_data_count = int(requests.get(url+".json?$query=SELECT COUNT(*)").json()[0]["COUNT"])

            #Determine how many data should be download based on available_data_count and max_data_count
            nums_data_to_download = max_data_count if (max_data_count< available_data_count) else available_data_count

            #Print out the process
            print("INFO: Downloading %s data from \"%s\"..." %(nums_data_to_download, url))

            #Start downloading data and convert them to csv
            with closing(requests.get(url+".csv?$limit="+str(nums_data_to_download),stream=True)) as response:
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
         #Print out the process
        print("INFO: Exporting RDF graph formatted as %s..." % format)

        #If export format is set as CSV
        if format=="csv":

            #Export to a file
            if destination:

                #Create base filepath
                paths= destination.split('.')
                filename = paths[len(paths)-2]

                #Create filepath for arrest reports csv
                paths[len(paths)-2]=filename+"_arrest_reports"
                arrest_reports_filepath = '.'.join(paths)

                #Create filepath for crime report csv
                paths[len(paths)-2]=filename+"_crime_reports"
                crime_reports_filepath = '.'.join(paths)

                #Write arrest reports csv CSV to file
                with open(arrest_reports_filepath, "wt") as fp:
                    writer = csv.writer(fp,delimiter=",")
                    writer.writerows(self.arrest_reports_dataset)

                #Write crime report csv to file
                with open(crime_reports_filepath, "wt") as fp:
                    writer = csv.writer(fp,delimiter=",")
                    writer.writerows(self.crime_reports_dataset)
            
            #Export as variables
            else:
                return self.arrest_reports_dataset, self.crime_reports_dataset
        #If export as other formats
        else:
            #Export to a file
            if destination:
                self.graph.serialize(destination=destination,format=format)
            #Export as variables
            else:
                return self.graph.serialize(format=format).decode("utf-8")

    
    def _add_arrest_reports_to_graph(self, arrest_reports, graph, namespace):
        """Add arrest reports dataset to the RDF graph

        Args:
            arrest_reports_dataset (string): a CSV contains arrest reports with well-formatted data
            graph (Graph): an RDF graph
            namespace (string): base namespace for all resources

        Returns:
            [Graph]: an RDF graph contains data from the arrest report dataset
        """

        #Print out the process
        print("INFO: Add arrest reports dataset to graph...")
     
        #Looping through everyone row of arrest reports
        for i in range(1, len(arrest_reports)): 

            #Determine how many instances of Report already exist in the graph
            number_report = len(list(graph.subject_objects(predicate=namespace["hasID"])))

            #Add a new instances of ArrestReport class and fill its properties that it inherent from Report class 
            graph.add((namespace["Report#" + str(number_report)], RDF.type, namespace["ArrestReport"]))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasID"], Literal(arrest_reports[i][0], datatype=XSD.integer)))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasDate"], Literal(arrest_reports[i][2], datatype=XSD.date)))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasTime"], Literal(arrest_reports[i][3], datatype=XSD.time)))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasReporType"], Literal(arrest_reports[i][1], datatype=XSD.string)))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasArrestType"], Literal(arrest_reports[i][12], datatype=XSD.string)))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasDispositionDescription"], Literal(arrest_reports[i][15], datatype=XSD.string)))

            #Add an instance of Person class
            #Check if an instance of Person class already exist in the graph
            people_age = set(graph.subjects(predicate = namespace["hasAge"], object=Literal(arrest_reports[i][7], datatype=XSD.integer)))
            people_sex = set(graph.subjects(predicate = namespace["hasSex"], object=Literal(arrest_reports[i][8], datatype=XSD.string)))
            people_decendent = set(graph.subjects(predicate = namespace["hasDescendent"], object=Literal(arrest_reports[i][9], datatype=XSD.string)))
            person = list(people_age & people_sex & people_decendent)

            # Return the number of instances of Person class
            number_person = len(list(graph.subject_objects(predicate=namespace["hasAge"])))

            #Create a new instance of Person class            
            if(len(person) == 0): 
                # add to Person
                graph.add((namespace["Person#" + str(number_person)], RDF.type, namespace["Person"]))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasAge"], Literal(arrest_reports[i][7], datatype=XSD.integer)))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasSex"], Literal(arrest_reports[i][8], datatype=XSD.string)))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasDescendent"], Literal(arrest_reports[i][9], datatype=XSD.string)))
                person = namespace["Person#" + str(number_person)]
            
            #Reuse an existing instance of Person class
            else: 
                person = person[0]
            
            #Add an instance of Location class
            #Check if an instance of Location class already exist in the graph
            location_reporting_dist = set(graph.subjects(predicate = namespace["hasReportingDistrictNumber"], object=Literal(arrest_reports[i][6], datatype=XSD.integer)))
            location_areaID = set(graph.subjects(predicate = namespace["hasAreaID"], object=Literal(arrest_reports[i][4], datatype=XSD.integer)))
            location_area_name = set(graph.subjects(predicate = namespace["hasAreaName"], object=Literal(arrest_reports[i][5], datatype=XSD.string)))
            location_address = set(graph.subjects(predicate = namespace["hasAddress"], object=Literal(arrest_reports[i][16], datatype=XSD.string)))
            location_cross_street = set(graph.subjects(predicate = namespace["hasCrossStreet"], object=Literal(arrest_reports[i][17], datatype=XSD.string)))
            location_lat = set(graph.subjects(predicate = namespace["hasLatitude"], object=Literal(arrest_reports[i][18], datatype=XSD.double)))
            location_lon = set(graph.subjects(predicate = namespace["hasLongtitude"], object=Literal(arrest_reports[i][19], datatype=XSD.double)))
            location = list(location_reporting_dist & location_areaID & location_area_name & location_address & location_cross_street & location_lat & location_lon)
            
            #Return the number of instances of Location class
            number_location = len(list(graph.subject_objects(predicate=namespace["hasAreaID"])))

            #Create a new instance of Location class
            if(len(location) == 0): 
                # no location
                graph.add((namespace["Location#" + str(number_location)], RDF.type, namespace["Location"]))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasReportingDistrictNumber"], Literal(arrest_reports[i][6], datatype=XSD.integer)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAreaID"], Literal(arrest_reports[i][4], datatype=XSD.integer)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAreaName"], Literal(arrest_reports[i][5], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAddress"], Literal(arrest_reports[i][16], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasCrossStreet"], Literal(arrest_reports[i][17], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasLatitude"], Literal(arrest_reports[i][18], datatype=XSD.double)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasLongtitude"], Literal(arrest_reports[i][19], datatype=XSD.double)))
                location = namespace["Location#" + str(number_location)]
            
            #Reuse an exisiting instance of Location class
            else: 
                location = location[0]            

            #Add an instance of Booking class
            #Check if an instance of Booking class already exist in the graph
            booking_date = set(graph.subjects(predicate = namespace["hasBookingDate"], object=Literal(arrest_reports[i][21], datatype=XSD.date)))
            booking_time = set(graph.subjects(predicate = namespace["hasBookingTime"], object=Literal(arrest_reports[i][22], datatype=XSD.time)))
            booking_location = set(graph.subjects(predicate = namespace["hasBookingLocation"], object=Literal(arrest_reports[i][23], datatype=XSD.string)))
            booking_code = set(graph.subjects(predicate = namespace["hasBookingCode"], object=Literal(arrest_reports[i][24], datatype=XSD.integer)))
            booking = list(booking_date & booking_time & booking_location & booking_code)

            #Return the number of instances of Location class
            number_booking = len(list(graph.subject_objects(predicate=namespace["hasBookingCode"])))

            #Create a new instance of Booking class
            if(len(booking) == 0): 
                graph.add((namespace["Booking#" + str(number_booking)], RDF.type, namespace["Booking"]))
                graph.add((namespace["Booking#" + str(number_booking)], namespace["hasBookingDate"], Literal(arrest_reports[i][21], datatype=XSD.date)))
                graph.add((namespace["Booking#" + str(number_booking)], namespace["hasBookingTime"], Literal(arrest_reports[i][22], datatype=XSD.time)))
                graph.add((namespace["Booking#" + str(number_booking)], namespace["hasBookingLocation"], Literal(arrest_reports[i][23], datatype=XSD.string)))
                graph.add((namespace["Booking#" + str(number_booking)], namespace["hasBookingCode"], Literal(arrest_reports[i][24], datatype=XSD.integer)))
                booking = namespace["Booking#" + str(number_booking)]
            
            #Reuse an existing instance of Booking class
            else: 
                booking = booking[0]
            
            #Add an instance of Charge class
            #Check if an instance of Charge class already exist in the graph
            charge_group_code = set(graph.subjects(predicate = namespace["hasChargeGroupCode"], object=Literal(arrest_reports[i][10], datatype=XSD.integer)))
            charge_group_description = set(graph.subjects(predicate = namespace["hasChargeGroupDescription"], object=Literal(arrest_reports[i][11], datatype=XSD.string)))
            charge_code = set(graph.subjects(predicate = namespace["hasChargeCode"], object=Literal(arrest_reports[i][13], datatype=XSD.string)))
            charge_description = set(graph.subjects(predicate = namespace["hasChargeDescription"], object=Literal(arrest_reports[i][14], datatype=XSD.string)))
            charge = list(charge_group_code & charge_group_description & charge_code & charge_description)

            #Return the number of instances of Location class
            number_charge = len(list(graph.subject_objects(predicate=namespace["hasChargeCode"])))
            
            #Create a new instance of Charge class
            if(len(charge) == 0): 
                graph.add((namespace["Charge#" + str(number_charge)], RDF.type, namespace["Charge"]))
                graph.add((namespace["Charge#" +str(number_charge)], namespace["hasChargeGroupCode"], Literal(arrest_reports[i][10], datatype=XSD.integer)))
                graph.add((namespace["Charge#" +str(number_charge)], namespace["hasChargeGroupDescription"], Literal(arrest_reports[i][11], datatype=XSD.string)))
                graph.add((namespace["Charge#" +str(number_charge)], namespace["hasChargeCode"], Literal(arrest_reports[i][13], datatype=XSD.integer)))
                graph.add((namespace["Charge#" +str(number_charge)], namespace["hasChargeDescription"], Literal(arrest_reports[i][14], datatype=XSD.string)))
                charge = namespace["Charge#" + str(number_charge)]
            
            #Reuse an existing instance of Charge class
            else: 
                charge = charge[0]

            #Add to report
            graph.add((namespace["Report#" + str(number_report)], namespace["hasPerson"], person))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasLocation"], location))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasBooking"], booking))
            graph.add((namespace["Report#" + str(number_report)], namespace["hasCharge"], charge))
       
        return graph


    def _add_crime_reports_to_graph(self, crime_reports, graph, namespace):
        """Add crime reports dataset to the RDF graph

        Args:
            crime_reports_dataset (string): a CSV contains crime reports with well-formatted datapoints
            graph (Graph): an RDF graph
            namespace (string): base namespace for all resources

        Returns:
            [Graph]: an RDF graph contains data from the crime report dataset
        """
        #Print out the process
        print("INFO: Add crime reports dataset to graph...")

        #Define new columns 
        colNames = ['ReportID', 'DataReported', 'DateOCC', 'TimeOCC', 'Area',
            'AreaName', 'ReportDistrict', 'Part-1-2', 'CrimeCommited',
            'CrimeDescription', 'Mocodes', 'Age', 'SexCode',
            'DescendentCode', 'PremiseCode', 'PremiseDescription',
            'WeaponCode', 'WeaponDescription', 'Status',
            'StatusDescription', 'CrimCommited1', 'CrimCommited2',
            'CrimCommited3', 'CrimCommited4', 'location',
            'CrossStreet', 'lat', 'lon']

        #Convert csv to panda dataframe
        df = pd.DataFrame (crime_reports[1:], columns=colNames)

        #Determine the number of instances of Report class
        starting_report_num = len(list(graph.subject_objects(predicate=namespace["hasID"])))

        #ID
        dr_no_list = df['ReportID']
        for index, value in dr_no_list.items():
            graph.add((namespace["Report#" + str(index+starting_report_num)], RDF.type, namespace["CrimeReport"]))
            graph.add((namespace["Report#" + str(index+starting_report_num)], namespace["hasID"], Literal(value, datatype=XSD.integer)))

        
        # Person
        age_list = df['Age']
        sex_list = df['SexCode']
        descendent_list = df['DescendentCode']

        for i in range(0,len(age_list)):

            #Check if an instance of Person class already exist in the graph
            people_age = set(graph.subjects(predicate = namespace["hasAge"], object=Literal(age_list[i], datatype=XSD.integer)))
            people_sex = set(graph.subjects(predicate = namespace["hasSex"], object=Literal(sex_list[i], datatype=XSD.string)))
            people_decendent = set(graph.subjects(predicate = namespace["hasDescendent"], object=Literal(descendent_list[i], datatype=XSD.string)))
           
            #Give all the triples with age, sex, and decendent
            person = list(people_age & people_sex & people_decendent)
            
            #Return the number of instances of Person class
            number_person = len(list(graph.subject_objects(predicate=namespace["hasAge"])))
            
            #Create a new instance of Person class
            if(len(person) == 0): 
                graph.add((namespace["Person#" + str(number_person)], RDF.type, namespace["Person"]))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasAge"], Literal(age_list[i], datatype=XSD.integer)))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasSex"], Literal(sex_list[i], datatype=XSD.string)))
                graph.add((namespace["Person#" + str(number_person)], namespace["hasDescendent"], Literal(descendent_list[i], datatype=XSD.string)))
                person = namespace["Person#" + str(number_person)]
            
            #Reuse an existing instance of Person
            else: 
                person = person[0];

            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasPerson"], person));

        
        # Time Occured
        time_list = df['TimeOCC']

        for index, value in time_list.items():
            graph.add((namespace["Report#" + str(index + starting_report_num)], namespace["hasTime"], Literal(value, datatype=XSD.time)))
        
        
        # Date Occured
        date_list = df['DateOCC']

        for index, value in date_list.items():
            graph.add((namespace["Report#" + str(index + starting_report_num)], namespace["hasDate"], Literal(value, datatype=XSD.date)))

        
        # Location
        reportDist = df['ReportDistrict']
        areaList = df['Area']
        areaNameList = df['AreaName']
        locationList = df['location']
        crossStreetList = df['CrossStreet']
        latList = df['lat']
        lonList = df['lon']

        for i in range(0,len(reportDist)):

            #Check if an instance of Location class already exist in the graph
            reportingDisct = set(graph.subjects(predicate = namespace["hasReportingDisctrictNumber"], object=Literal(reportDist[i], datatype=XSD.integer)))
            areaID = set(graph.subjects(predicate = namespace["hasAreaID"], object=Literal(areaList[i], datatype=XSD.string)))
            areName = set(graph.subjects(predicate = namespace["hasAreaName"], object=Literal(areaNameList[i], datatype=XSD.string)))
            addy = set(graph.subjects(predicate = namespace["hasAddress"], object=Literal(locationList[i], datatype=XSD.string)))
            crossStreet = set(graph.subjects(predicate = namespace["hasCrossStreet"], object=Literal(crossStreetList[i], datatype=XSD.string)))
            lati = set(graph.subjects(predicate = namespace["hasLatitude"], object=Literal(latList[i], datatype=XSD.double)))
            longi = set(graph.subjects(predicate = namespace["hasLongitude"], object=Literal(lonList[i], datatype=XSD.double)))

            #Give all the triples with reporting disct, area id, area name, address, cross street, latitude, and longtitude
            loctions = list(reportingDisct & areaID & areName & addy & crossStreet & lati & longi)
            
            #Return the number of instances of Location class
            number_location = len(list(graph.subject_objects(predicate=namespace["hasAreaID"])))
            
            #Create a new instance of Location class
            if(len(loctions) == 0): 
                # add to Location
                graph.add((namespace["Location#" + str(number_location)], RDF.type, namespace["Location"]))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasReportingDisctrictNumber"], Literal(reportDist[i], datatype=XSD.integer)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAreaID"], Literal(areaList[i], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAreaName"], Literal(areaNameList[i], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasAddress"], Literal(locationList[i], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasCrossStreet"], Literal(crossStreetList[i], datatype=XSD.string)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasLatitude"], Literal(latList[i], datatype=XSD.double)))
                graph.add((namespace["Location#" + str(number_location)], namespace["hasLongitude"], Literal(lonList[i], datatype=XSD.double)))
                loctions = namespace["Location#" + str(number_location)]
            
            #Reuse an existing instance of Location class
            else: 
                loctions = loctions[0];
            
            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasLocation"], loctions));

        
        # Date Reported
        date_reported = df['DataReported']

        for index, value in date_reported.items():
            graph.add((namespace["Report#" + str(index + starting_report_num)], namespace["hasDateReported"], Literal(value, datatype=XSD.date)))

        
        # Date Reported
        mocodesList = df['Mocodes']

        for index, value in mocodesList.items():
            graph.add((namespace["Report#" + str(index + starting_report_num)], namespace["hasMocodes"], Literal(value, datatype=XSD.string)))

       
        # Part 1-2
        part_1_2 = df['Part-1-2']

        for index, value in part_1_2.items():
            graph.add((namespace["Report#" + str(index + starting_report_num)], namespace["hasPart1-2"], Literal(value, datatype=XSD.integer)))

        
        # Premise
        premiseCodeList = df['PremiseCode']
        premiseDescriptionList = df['PremiseDescription']

        for i in range(0,len(premiseCodeList)):

            #Check if an instance of Premise class already exist in the graph
            premiseCode = set(graph.subjects(predicate = namespace["hasPremiseCode"], object=Literal(premiseCodeList[i], datatype=XSD.integer)))
            premiseDesc = set(graph.subjects(predicate = namespace["hasPremiseDescription"], object=Literal(premiseDescriptionList[i], datatype=XSD.string)))

            #Give all the triples with premise code and premise description
            premises = list(premiseDesc & premiseCode)
            
            #Return the number of instances of Premise class
            number_premise = len(list(graph.subject_objects(predicate=namespace["hasPremiseCode"])))
            
            #Create a new instance of Premise class
            if(len(premises) == 0): 
                # add to Location
                graph.add((namespace["Premise#" + str(number_premise)], RDF.type, namespace["Premise"]))
                graph.add((namespace["Premise#" + str(number_premise)], namespace["hasPremiseCode"], Literal(premiseCodeList[i], datatype=XSD.integer)))
                graph.add((namespace["Premise#" + str(number_premise)], namespace["hasPremiseDescription"], Literal(premiseDescriptionList[i], datatype=XSD.string)))
                premise = namespace["Premise#" + str(number_premise)]
            
            #Reuse an existing instance of Premise class
            else: 
                premise = premises[0]

            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasPremise"], premise))

        # Weapon
        weaponUsedList = df['WeaponCode']
        weaponDescriptionList = df['WeaponDescription']

        for i in range(0,len(weaponUsedList)):

            #Create a new instance of Weapon class
            weaponCode = set(graph.subjects(predicate = namespace["hasWeaponCode"], object=Literal(weaponUsedList[i], datatype=XSD.integer)))
            weaponDesc = set(graph.subjects(predicate = namespace["hasWeaponDescription"], object=Literal(weaponDescriptionList[i], datatype=XSD.string)))

            #Give all the triples with weapon cdoe and weapon description
            weapons = list(weaponDesc & weaponCode)

            #Create a new instance of Weapon class
            number_weapon = len(list(graph.subject_objects(predicate=namespace["hasWeaponCode"])))
            
            #Create a new instance of Weapon class
            if(len(weapons) == 0): 
                # add to Location
                graph.add((namespace["Weapon#" + str(number_weapon)], RDF.type, namespace["Weapon"]))
                graph.add((namespace["Weapon#" + str(number_weapon)], namespace["hasWeaponCode"], Literal(weaponUsedList[i], datatype=XSD.integer)))
                graph.add((namespace["Weapon#" + str(number_weapon)], namespace["hasWeaponDescription"], Literal(weaponDescriptionList[i], datatype=XSD.string)))
                weapons = namespace["Weapon#" + str(number_weapon)]
            
            #Reuse an existing instance of Weapon class
            else: 
                weapons = weapons[0]

            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasWeapon"], weapons))


        # Status
        statusList = df['Status']
        statusDescriptionList = df['StatusDescription']

        for i in range(0,len(statusList)):

            #Check if an instance of Status class already exist in the graph
            statusCode = set(graph.subjects(predicate = namespace["hasStatusCode"], object=Literal(statusList[i], datatype=XSD.string)))
            statusDesc = set(graph.subjects(predicate = namespace["hasStatusDescription"], object=Literal(statusDescriptionList[i], datatype=XSD.string)))

            #Give all the triples with status code and status description
            status = list(statusDesc & statusCode)
            
            #Return the number of instances of Status class
            number_status = len(list(graph.subject_objects(predicate=namespace["hasStatusCode"])))
            
            #Create a new instance of Status class
            if(len(status) == 0): 
                # add to Location
                graph.add((namespace["Status#" + str(number_status)], RDF.type, namespace["Status"]))
                graph.add((namespace["Status#" + str(number_status)], namespace["hasStatusCode"], Literal(statusList[i], datatype=XSD.string)))
                graph.add((namespace["Status#" + str(number_status)], namespace["hasStatusDescription"], Literal(statusDescriptionList[i], datatype=XSD.string)))
                status = namespace["Status#" + str(number_status)]
           
            #Reuse an existing instance of Status class
            else: 
                status = status[0]

            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasStatus"], status))


        # Crimes
        CrimCommitedList = df['CrimeCommited']
        CrimeDescriptionList = df['CrimeDescription']
        CrimCommited1List = df['CrimCommited1']
        CrimCommited2List = df['CrimCommited2']
        CrimCommited3List = df['CrimCommited3']
        CrimCommited4List = df['CrimCommited4']

        for i in range(0,len(reportDist)):

            #Check if an instance of Crime class already exist in the graph
            crimeCommitted = set(graph.subjects(predicate = namespace["hasCrimeCommitted"], object=Literal(CrimCommitedList[i], datatype=XSD.integer)))
            crimeCrimmitedDescription = set(graph.subjects(predicate = namespace["hasCrimeCrimmitedDescription"], object=Literal(CrimeDescriptionList[i], datatype=XSD.string)))
            crimeCommited1 = set(graph.subjects(predicate = namespace["hasCrimeCommited1"], object=Literal(CrimCommited1List[i], datatype=XSD.integer)))
            crimeCommited2 = set(graph.subjects(predicate = namespace["hasCrimeCommited2"], object=Literal(CrimCommited2List[i], datatype=XSD.integer)))
            crimeCommited3 = set(graph.subjects(predicate = namespace["hasCrimeCommited3"], object=Literal(CrimCommited3List[i], datatype=XSD.integer)))
            crimeCommited4 = set(graph.subjects(predicate = namespace["hasCrimeCommited4"], object=Literal(CrimCommited4List[i], datatype=XSD.integer)))

            #Give all the triples with mutiple crime committed
            crimes = list(crimeCommitted & crimeCrimmitedDescription & crimeCommited1 & crimeCommited2 & crimeCommited3 & crimeCommited4)
            
            #Return the number of instances of Crime class
            number_crime_commited = len(list(graph.subject_objects(predicate=namespace["hasCrimeCommitted"])))

            #Return the number of instances of Crime class
            if(len(crimes) == 0): 
                # add to Location
                graph.add((namespace["Crime#" + str(number_crime_commited)], RDF.type, namespace["Crime"]))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCommitted"], Literal(CrimCommitedList[i], datatype=XSD.integer)))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCrimmitedDescription"], Literal(CrimeDescriptionList[i], datatype=XSD.string)))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCommited1"], Literal(CrimCommited1List[i], datatype=XSD.integer)))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCommited2"], Literal(CrimCommited2List[i], datatype=XSD.integer)))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCommited3"], Literal(CrimCommited3List[i], datatype=XSD.integer)))
                graph.add((namespace["Crime#" + str(number_crime_commited)], namespace["hasCrimeCommited4"], Literal(CrimCommited4List[i], datatype=XSD.integer)))
                crimes = namespace["Crime#" + str(number_crime_commited)]
            
            #Reuse an existing instance of Crime class
            else: 
                crimes = crimes[0];

            graph.add((namespace["Report#" + str(i + starting_report_num)], namespace["hasCrime"], crimes));

        return graph
