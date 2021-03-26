
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
