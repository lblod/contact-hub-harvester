# Contact Hub Harvester

Install the requirements

`pip install -r requirements.txt`

To run the mapping for each file, it depends on the type of file. The general command is:

`python3 app.py type_file path/to/input/file mode`

| type_file   |  mode   |
|-------------|---------|
|org          |  dev    |
|contact      |  qa     |
|worship      |  local  |
|central      |         |
|national     |         |
|codelist     |         |

If type_file is codelist, do not include an input file and mode.

Three other files used in the cleansing process need to be in the input folder.

Create an output folder to store the files in ttl.


