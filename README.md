## Unmixing concordia

This is a Python script accompanying the paper "Unmixing U-Pb ages from core-rim mixtures". 

#### Requirements

Requires Python 3 (tested on version 3.6.9) and the following packages:
- matplotlib version 0.13 or later
- SciPy -- version 1.4.1 or later
- uncertainties -- version 3.1.2 or later
- soerp -- version 0.9.6 or later
- mcerp -- version 0.12 or later

All of these packages are available via PIP and the following line should install all of them:
```
pip install matplotlib scipy uncertainties soerp mcerp
```

#### Configuration

Before running the program you should open the file `config.py` and adjust any settings as desired. For example you can set the desired number of significant figures used, whether to use absolute or percentage errors and whether to use 1 or 2 standard deviations.

#### Running in CSV mode

In this mode the program takes a CSV file as input which includes the following columns:
1. Rim age (in Ma)
2. Rim age error
3. Mixed point U238/Pb206 ratio
4. Mixed point U238/Pb206 ratio error
5. Mixed point Pb207/Pb206 ratio
6. Mixed point Pb207/Pb206 ratio error

These columns need not be in order and the CSV file may contain other columns. Both the location of the columns and the separator used should be configured in `config.py` before hand.

The program may then be run as:
```
python unmix_concordia.py csv --input=X --output=Y
```
where `X` is the location of the input file (either relative or absolute) and `Y` is the desired location of the output. The output is another CSV file that contains all the columns of the input file with an 9 additional columns:
1. Reconstructed age
2. Reconstructed age (+error)
3. Reconstructed age (-error)
4. Reconstructed U238/Pb206 ratio
5. Reconstructed U238/Pb206 ratio (+error)
6. Reconstructed U238/Pb206 ratio (-error)
7. Reconstructed Pb207/Pb206 ratio
8. Reconstructed Pb207/Pb206 ratio (+error)
9. Reconstructed Pb207/Pb206 ratio (-error)

Optionally the extra flag `-f` or `--figures` may be added to the command:
```
python unmix_concordia.py csv -f --input=X --output=Y
```
In addition to the main output file, the program will also generate a figure for each line in the CSV file underneath the folder `Y/` (e.g. for `Y`=`output.csv` then a new folder `output/` will be created ).

#### Running in interactive mode

Interactive mode allows to explore a single error calculation and may be run as follows:
```
python unmix_concordia.py interactive
```