# MASHix


### Description

This script runs MASH, making a parwise comparisons between sequences in input (fasta) file(s).

Note: each header in fasta is considered a reference.

### Dependencies:

* **Mash** - You can download mash version 1.1.1 directly here: [linux](https://github.com/marbl/Mash/releases/download/v1.1.1/mash-Linux64-v1.1.1.tar.gz) and [OSX](https://github.com/marbl/Mash/releases/download/v1.1.1/mash-OSX64-v1.1.1.tar.gz). Other releases were not tested but may be downloaded in Mash git [releases page](https://github.com/marbl/Mash/releases).

* **Postgresql** - This script uses Postgres database to store the database - [releases page](https://www.postgresql.org/download/)

To install all other dependencies just run: _pip install -r requirements.txt_

Note: This script exports a JSON file to be loaded with [VivaGraphJS](https://github.com/anvaka/VivaGraphJS) in order to plot distances between genomes (example file is provided in modules/import\_to\_vivagraph.json). Altough, there is no need to load additional modules since they are provided along with the _pATLAS.html_ in modules.


The first thing you have to do is run MASHix.py in order to calculate distances between all the genomes in a fasta, using [MASH](http://mash.readthedocs.io/en/latest/). MASHix.py does all the processing, thus you don't need to worry about fasta concatenation or header processing. Also, it runs all MASH commands required to obtain a pairwise matrix (though it do not exports one because it will not be human readable for large datasets).

### Options:

#### Main options:

```
'-i','--input_references' - 'Provide the input fasta files to parse. This will inputs will be joined in a master fasta.'

'-o','--output' - 'Provide an output tag'

'-t', '--threads' - 'Provide the number of threads to be used'
```

#### MASH related options:
```
'-k','--kmers' - 'Provide the number of k-mers to be provided to mash sketch. Default: 21'

'-p','--pvalue' - 'Provide the p-value to consider a distance significant. Default: 0.05'

'-md','--mashdist' - 'Provide the maximum mash distance to be parsed to the matrix. Default:0.1'
```

#### Other options:

```
'-no_rm', '--no-remove' - 'Specify if you do not want to remove the output concatenated fasta.'

'-hist', '--histograms' - 'Checks the distribution of distances values ploting histograms.'
```

---

### Database customization:

#### I don't like database name! How do I change it?

Go to db_manager/config_default.py and edit the [line 5](https://github.com/tiagofilipe12/MASHix/blob/master/db_manager/config_default.py#L5):

```python
SQLALCHEMY_DATABASE_URI = 'postgresql:///<custom_database_name>'
```

#### I don't like table name inside database! How do I change it?

Go to db_manager/db_app/models.py and edit the [line 7](https://github.com/tiagofilipe12/MASHix/blob/master/db_manager/db_app/models.py#L7):

```python
 __tablename__ = "<custom_table_name>"
```

---

### Database migration from one server to another

#### Database export

```
pg_dump <db_name> > <file_name.sql>
```

#### Database import

```
psql -U <user_name> -d <db_name> -f <file_name.sql>
```

---

### Supplementary scripts

#### taxa_fetch.py

This script is used to parse ncbi taxonomy to retrieve families and orders given an input list of genera of bacteria (list generated also by MASHix.py as ".lst" file).

```
taxa_fetch.py <names.dmp> <nodes.dmp> <genera.lst>
```
