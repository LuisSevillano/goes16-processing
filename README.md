# Processing GOES-16 images

Python scripts for downloading and processing data from NASA's GOES-16. This repository contains two scripts, one for downloading data and another for processing all the `*.nc` files in a folder.

The scripts are designed to process all the data for a specific day in the format `2021-08-27` ("%Y-%m-%d") with the aim of creating a final animation with each of the images generated. GOES-16 generates a image every 10 minutes.

For downloading the data for August 27, 2021 you should run:

```python
# python3 download_goes_from_aws.py date output-path
python3 download_goes_from_aws.py 2021-08-27 files/2021-08-27
```

`download_goes_from_aws.py` will start downloading all the files available for the given day using `multiprocessing.dummy` (4 files simultaneously but you can change it in code). The script downloads the files to the root folder and once the download is finished it moves it to the requested folder.

Once the download is finished you can proceed to process all the files:

```python
# python3 fulldisk-folder.py path
python3 fulldisk-folder.py /Users/<USER>/Documents/projects/goes16-processing/files/2021-08-27
```

`fulldisk-folder.py` will search for all the files in the path it receives as an argument (It doesn't filter by file extension, if you have any other file than `*.nc` the script will fail) and will generate a `png` with a timestamp for each of them.

Each generated file will look similar to the following:

![goes-16](https://i.ibb.co/wNZ8mZ4/OR-ABI-L2-MCMIPF-M6-G16-s20212391340205-e20212391349524-c20212391350021.png)

Thanks to [Unidata](https://www.unidata.ucar.edu/), much of the code comes from their great python tutorials.

## Working with virtual enviroments

Virtualenv is a tool that lets you create an isolated Python environment for your project. It creates an environment that has its own installation directories
To install it:

```
pip install virtualenv
```

Go to your project folder and create it:

```
cd goes16-processing/
virtualenv venv
```

To activate it:

```
source venv/bin/activate
```

To leave the virtual environment run:

```
deactivate
```

[Source](https://sourabhbajaj.com/mac-setup/Python/virtualenv.html).
