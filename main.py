from Backend.rdf import RDF_Graph
import os

#Variables
filename = os.path.abspath("./output.rdf")
arrest_reports_url = "https://data.lacity.org/resource/amvf-fr72"
crime_reports_url = "https://data.lacity.org/resource/2nrs-mtv8"
max_dataset_size = 1000
done = False
sucess_option_1 = False
sucess_option_2 = False
sucess_option_3 = False

#CLI logic
while (not done):

    #Print instructions
    print("\u0332".join("RDF Generator"))

    print(" This program will: \n     \u2022 Download datasets for Arrest Reports and Crime Reports \n     \u2022 Generate RDF graph from both reports \n     \u2022 Save RDF graph to a file")

    print(" Parameters: \n     \u2022 Arrest Reports URL: %s \n     \u2022 Crime Reports URL: %s \n     \u2022 RDF Filename: %s \n     \u2022 Max Dataset Size: %s" % (arrest_reports_url, crime_reports_url, filename, max_dataset_size))

    print(" Options: \n     1. Run \n     2. Modify filename \n     3. Modify max dataset size \n     4. Exit")

    #User's input feedback
    if sucess_option_1:
        print("INFO: Successfully generate RDF file...")
        sucess_option_1=False
    elif sucess_option_2:
        print("INFO: Successfully modify filename")
        sucess_option_2=False
    elif sucess_option_3:
        print("INFO: Successfully modify max dataset size")
        sucess_option_3=False

    #Obtain user's input
    user_input = input("Enter an option: ")

    #Option 1: Generate RDF and save to file
    if (user_input=="1"):
        graph = RDF_Graph(arrest_reports_url=arrest_reports_url, crime_reports_url=crime_reports_url, max_dataset_size=max_dataset_size)
        graph.export(filename)
        sucess_option_1=True
        pass

    #Option 2: Modify filename
    elif (user_input=="2"):
        filename = input("Enter filename: ")
        filename = os.path.abspath(filename)
        sucess_option_2=True
        pass

    #Option 3: Modify max dataset size
    elif (user_input=="3"):
        max_dataset_size = input("Enter size: ")
        sucess_option_3=True
        pass

    #Option 4: Exit
    elif (user_input=="4"):
        done = True
        pass

    #Clear terminal to prevent overcrowded 
    os.system('cls' if os.name == 'nt' else 'clear')

