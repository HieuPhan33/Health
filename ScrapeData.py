import urllib.request
import requests
import json
import re
from bs4 import BeautifulSoup
import pprint
import csv
import pandas as pd
pp = pprint.PrettyPrinter(indent=3)
# Prompt symptomp term
print("Enter the symptomp you would like to extract data")
input_symptomp = input()
# Formatting string process to pass to url
list_str = input_symptomp.lower().split()
# Formatted symptomp str
symptomp = "-".join(list_str)
url = 'https://www.healthline.com/symptom/'+str(symptomp)
print(url)
try:
    with urllib.request.urlopen('https://www.healthline.com/symptom/dizziness') as web:
        soup = BeautifulSoup(web.read(), 'lxml')
    script = soup.find_all("script")
    # Looking for the variable NEXT_DATA holding needed information
    input = filter(lambda x: x.string and "__NEXT_DATA__" in x.string, script).__next__()
    list_var = str(input).split("\n")
    # Further extracting our needed variable __NEXT_DATA__
    input = filter(lambda x: x and "__NEXT_DATA__" in x, list_var).__next__()
    # the input is __NEXT_DATA__ = {...}
    # => We only need the json string on the right hand side
    input = input.split("=", 1)
    jsonStr = input[1]
    data = json.loads(jsonStr)
    relatedSyms = data['props']['relatedSymptoms']
    relatedSyms = [d['cfn'] for d in relatedSyms]
    print("The related symptomps of "+str(symptomp))
    pp.pprint(relatedSyms)
    # Write into related symptomps to csv file stored at symptomp.csv
    with open((str(symptomp)+".csv"),'w') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(relatedSyms)
    CombinationSyms = dict()
    # Format each symptomp string to pass to URL for further search
    format_syms = [x.replace(" ", "-").lower() for x in relatedSyms]
    not_found_subsyms = []
    for subsym in format_syms:
        try:
            with urllib.request.urlopen('https://www.healthline.com/symptom/' + str(subsym) + '/' + str(symptomp)) as web:
                soup = BeautifulSoup(web.read(), 'lxml')
            sub_script=soup.find_all("script")
            input = filter(lambda x: x.string and "__NEXT_DATA__" in x.string, sub_script).__next__()
            list_var = str(input).split("\n")
            # Further extracting our needed variable __NEXT_DATA__
            input = filter(lambda x: x and "__NEXT_DATA__" in x, list_var).__next__()
            input = input.split("=", 1)
            jsonStr = input[1]
            data = json.loads(jsonStr)
            items = data['props']['items']
            diseases = [d['title'][0] for d in items]
            CombinationSyms[subsym] = diseases
        # If we could not get response from the website, data might be not available
        except urllib.error.HTTPError:
            not_found_subsyms.append(subsym)
            pass
    # Write combination of symptomps into symptomp_comb.csv
    with open((str(symptomp) + '_comb.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(CombinationSyms.keys())
        w.writerow(zip(*CombinationSyms.values()))
    #print out
    pp.pprint(CombinationSyms)
    for not_found in not_found_subsyms:
        print("No data yet about combination of "+str(symptomp)+" and "+not_found)
except urllib.error.HTTPError:
    print("Could not find symptomp '"+str(input_symptomp)+"' on the website or the service is not available at the moment")



