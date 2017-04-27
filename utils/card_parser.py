#!/usr/bin/env python2

from argparse import ArgumentParser
from subprocess import Popen, PIPE
import json
import os
import sys

## change path before loading modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from db_manager.db_app import db, models

'''
CARD fasta has proteins while NCBI plasmid sequences has nucl
This function allows to search in multiple blast databases
'''

def blast(input_query, list_of_dbs, threads):
    output_list = []
    for db in list_of_dbs:
        output_name = "{}_{}.txt".format(os.path.basename(
            input_query).split(".")[0], "_".join(os.path.basename(db).split(
            ".")[:-1]))
        blast_command = ["blastn",
                         "-query",
                         input_query,
                         "-db",
                         db,
                         "-outfmt",
                         "6",
                         "-evalue",
                         "0.000001",
                         "-num_threads",
                         str(threads),
                         "-out",
                         output_name]
        p = Popen(blast_command, stdout=PIPE, stderr=PIPE)
        print " ".join(blast_command)
        p.wait()
        stdout, stderr = p.communicate()
        print(stderr)
        output_list.append(output_name)
    return output_list

'''
Take blast results and search for similar entries and output a json entry for 
each NCBI accession number. Output json must have {ARO accession:ARO name, ...};
or instead of ARO something like Inc:, rep:, MOB:
'''

def output_json(dict_main_json, dic_length, output_list, infile):
    for blast_out in output_list:
        bout_file = open(blast_out, "r")
        for line in bout_file:
            list_json_entries=[]
            tab_split = line.split("\t")
            ARO_accession = tab_split[0].split("|")[-2].strip()
            ARO_NCBI_accession = tab_split[0].split("|")[1].strip()
            dic_key = "{}_{}".format(ARO_accession, ARO_NCBI_accession)
            ''' used column 8 with end of alignment in query since indels
            can be problematic when counting total alignment in column 4 '''
            length = float(tab_split[7].strip())
            if length > dic_length[dic_key]:
                print ARO_accession
                print length
                print dic_length[dic_key]
                break
            perc_fasta_cov = length/float(dic_length[dic_key])
            identity_fasta = float(tab_split[2].strip())
            NCBI_accession = tab_split[1]
            ARO_gb = tab_split[0].split("|")[1]
            ARO_name = tab_split[0].split("|")[5]
            list_json_entries=[ARO_accession, ARO_gb, ARO_name,
                               identity_fasta, perc_fasta_cov]
            if NCBI_accession in dict_main_json.keys():
                dict_main_json[NCBI_accession].append(list_json_entries)
            else:
                dict_main_json[NCBI_accession] = list_json_entries

    return dict_main_json

def json_dumping(dict_main_json):
    for k in dict_main_json.keys():
        row = models.Card(plasmid_id=k,
                          json_entry=json.dumps(dict_main_json[k]))
        db.session.add(row)
        db.session.commit()
    db.session.close()


# Function to obtain fasta lenght for a given entry

def get_length_fasta(dic_lenght, input_fasta_name):
    load_input_fasta = open(input_fasta_name, "r")
    seq_lenght = 0

    for line in load_input_fasta:
        if line.startswith(">"):
            line_split = line.split("|")
            if seq_lenght != 0:
                dic_lenght[stored_both] = seq_lenght + 1
            seq_lenght = 0
            stored_aro = line_split[-2].strip()
            stored_acc = line_split[1].strip()
            stored_both = "{}_{}".format(stored_aro, stored_acc)
        else:
            for x,char in enumerate(line.replace("\n","")):
                pass
            ## in the end we have to sum 1 since x starts at 0
            seq_lenght += x
    ## added for the final iteration of the loop
    if seq_lenght != 0:
        dic_lenght[stored_both] = seq_lenght + 1
    return dic_lenght

def main():
    parser = ArgumentParser(description="Searches gene entries in plasmids blast database and returns a json")
    parser.add_argument('-i', '--input', dest='input', required=True, nargs='+',
                        help='Provide the input fasta with genes to search for')
    parser.add_argument('-db', '--database', dest='database', required=True, nargs='+',
                        help='Provide the databases to be used by blast search')
    parser.add_argument('-p', '--processors', dest='processors', default='1',
                        help='Provide the number of threads to use')

    args = parser.parse_args()
    dbase = args.database
    threads = args.processors

    input_files = [f for f in args.input if f.endswith((".fas", ".fasta",
                                        ".fna", ".fsa", ".fa"))]
    dic_lenght = {}
    dict_main_json = {}
    for infile in input_files:
        #inputs_path = os.path.dirname(infile)
        dic_length = get_length_fasta(dic_lenght, infile)
        output_list = blast(infile, dbase, threads)
        dict_main_json_final = output_json(dict_main_json, dic_length,
                                         output_list,
                                     infile)

    json_dumping(dict_main_json_final)

if __name__ == "__main__":
    main()
    print "committing stuff to database"
    db.session.close()