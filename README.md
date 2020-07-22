![Curtin University: Timescales of Minerals Systems](./resources/logo-linear.png)

## U-Pb Unmixer

![Executables built](https://github.com/MatthewDaggitt/LeadLoss/workflows/Python%20executables/badge.svg)
[![DOI](https://zenodo.org/badge/252923972.svg)](https://zenodo.org/badge/latestdoi/252923972)

This program accompanies the paper "Unmixing U-Pb ages from core-rim mixtures". 

### Getting started 

#### Standalone executables

Standalone executables for Ubuntu, Windows and MacOS are available 
[here](https://github.com/Curtin-Timescales-of-Mineral-Systems/UPb-Unmixer/releases). These should be downloadable
and runnable without any further action.

* The executable may take up to 30 seconds to show the window the first time you run the program. Subsequent runs
should be faster.

* On Ubuntu it may be necessary to change the file permissions to make it executable. This can either be done via
`chmod 755` or by right clicking on the file and going `Properties` -> `Permissions`.

#### Running the Python code directly

The source code for each release is available 
[here](https://github.com/Curtin-Timescales-of-Mineral-Systems/UPb-Unmixer/releases). Download the source code, unzip
it into a folder. Open a terminal and navigate inside the unzipped folder. Run
```
pip install requirements.txt
```
in order to ensure you have the correct set of Python modules installed. Then to start the program run:
```
python src/UPb_Unmixer.py
```