#!/usr/bin/env python2

from argparse import ArgumentParser
import json
import os
import sys

## change path before loading modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from db_manager.db_app import db, models

def model_selector(selected_class):
    '''
    Function to make a selection of the output Class to be used to the database
    '''
    if selected_class == "card":
        model_class = models.Card
    #elif selected_class == "something":
    #    model_class = models.Something()
    #...
    return model_class

def output_json(dict_main_json, blast_out, card):
    '''
    This function outputs a dictionary of json entries per each Accession 
    number in database.
    '''
    bout_file = open(blast_out, "r")
    for line in bout_file:
        list_json_entries=[]
        tab_split = line.split("\t")
        NCBI_accession = tab_split[12]
        #ARO_NCBI_accession = tab_split[0].split("|")[1].strip()
        length = float(tab_split[13].strip())
        # The difference between query end and query start in alignment
        align_length = float(tab_split[7].strip()) - float(tab_split[6].strip())
        if align_length  > length :
            print("Warning. align length > length?!")
            print(line)
            break
        perc_fasta_cov = align_length/length
        identity_fasta = float(tab_split[2].strip())
        if card:
            ARO_accession = tab_split[0].split("|")[-2].strip()
            ARO_gb = tab_split[0].split("|")[1]
            ARO_name = tab_split[0].split("|")[5]
            list_json_entries=[ARO_accession, ARO_gb, ARO_name,
                            identity_fasta, perc_fasta_cov]
        else:
            print("No json formatting was specified, all db entry will be "
                  "outputted the first column of blast output")
            list_json_entries=[tab_split[0].strip(), identity_fasta,
                               perc_fasta_cov]
        if NCBI_accession in dict_main_json.keys():
            dict_main_json[NCBI_accession].append(list_json_entries)
        else:
            dict_main_json[NCBI_accession] = list_json_entries

    return dict_main_json

def json_dumping(dict_main_json, model_class):
    '''
    This function outputs each json entry in the dictionary to the postgres 
    database with each accession number as primary key and a list of arrays  
    '''
    for k in dict_main_json.keys():
        row = model_class(plasmid_id=k,
                          json_entry=json.dumps(dict_main_json[k]))
        db.session.add(row)
        db.session.commit()
    db.session.close()

def main():
    parser = ArgumentParser(description="Places blast outputs into postgres "
                                        "database. Note that blast outputs "
                                        "must be in format 6 and have two "
                                        "additional parameters at the end of "
                                        "default parameters - sacc and qlen."
                                        "For further information see HELPME.md")
    parser.add_argument('-i', '--input', dest='input', required=True,
                        nargs='+', help='Provide the input blast output '
                                        'files in tabular format')
    # when more than one class may be used this option has to pass to mutually
    # exclusive along with the new option
    parser.add_argument('-c', '--card', dest='card', action='store_true',
                        help='if the input query is card please use '
                             'this option.')

    args = parser.parse_args()
    input_files = [f for f in args.input]
    print("==============================================================")
    print("List of inputs:")
    print(input_files)
    print("==============================================================")
    dict_main_json = {}
    # more args can be passed to here depending on how many inputs will be
    # required to pass to the database
    if args.card:
        selected_class = "card"
    #elif something:
    #    selected_class = "something"
    #...
    else:
        print("Error, class unknown!")

    model_class = model_selector(selected_class)

    for blast_out in input_files:
        output_json(dict_main_json, blast_out, args.card)

    json_dumping(dict_main_json, model_class)

if __name__ == "__main__":
    main()