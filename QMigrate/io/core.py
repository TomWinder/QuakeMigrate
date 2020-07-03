# -*- coding: utf-8 -*-
"""
Module to handle input/output for QuakeMigrate.

"""

import logging
import pathlib

import pandas as pd
from obspy import read_inventory

import QMigrate.util as util


def stations(station_file, delimiter=","):
    """Alias for read_stations."""
    print("FutureWarning: function name has changed - continuing.")
    print("To remove this message, change:")
    print("\t'stations' -> 'read_stations'")

    return read_stations(station_file, delimiter)


def read_stations(station_file, delimiter=","):
    """
    Reads station information from file.

    Parameters
    ----------
    station_file : str
        Path to station file.
        File format (header line is REQUIRED, case sensitive, any order):
            Latitude, Longitude, Elevation (units of metres), Name
    delimiter : char, optional
        Station file delimiter (default ",").

    Returns
    -------
    stn_data : pandas DataFrame object
        Columns: "Latitude", "Longitude", "Elevation", "Name"

    Raises
    ------
    StationFileHeaderException
        Raised if the input file is missing required entries in the header.

    """

    stn_data = pd.read_csv(station_file, delimiter=delimiter)

    if ("Latitude" or "Longitude" or "Elevation" or "Name") \
       not in stn_data.columns:
        raise util.StationFileHeaderException

    stn_data["Elevation"] = stn_data["Elevation"].apply(lambda x: -1*x)

    # Ensure station names are strings
    stn_data = stn_data.astype({"Name": "str"})

    return stn_data


def read_response_inv(response_file, sac_pz_format=False):
    """
    Reads response information from file, returning it as a `obspy.Inventory`
    object.

    Parameters
    ----------
    response_file : str
        Path to response file.
        Please see the `obspy.read_inventory()` documentation for a full list
        of supported file formats. This includes a dataless.seed volume, a
        concatenated series of RESP files or a stationXML file.
    sac_pz_format : bool, optional
        Toggle to indicate that response information is being provided in SAC
        Pole-Zero files. NOTE: not yet supported.

    Returns
    -------
    response_inv : `obspy.Inventory` object
        ObsPy response inventory.

    Raises
    ------
    NotImplementedError
        If the user selects sac_pz_format.
    TypeError
        If the user provides a response file that is not readable by ObsPy.

    """

    if sac_pz_format:
        raise NotImplementedError("SAC_PZ is not yet supported. Please contact "
                                  "the QuakeMigrate developers.")
    else:
        try:
            response_inv = read_inventory(response_file)
        except TypeError as e:
            msg = (f"Response file not readable by ObsPy: {e}\n"
                   "Please consult the ObsPy documentation.")
            raise TypeError(msg)

    return response_inv


def read_vmodel(vmodel_file, delimiter=","):
    """
    Reads velocity model information from file.

    Parameters
    ----------
    vmodel_file : str
        Path to velocity model file.
        File format: (header line is REQUIRED, case sensitive, any order):
        Depth (units of metres), Vp, Vs (units of metres per second)
    delimiter : char, optional
        Velocity model file delimiter (default ",").

    Returns
    -------
    vmodel_data : pandas DataFrame object
        Columns: "Depth", "Vp", "Vs"

    Raises
    ------
    VelocityModelFileHeaderException
        Raised if the input file is missing required entries in the header.

    """

    vmodel_data = pd.read_csv(vmodel_file, delimiter=delimiter)

    if ("Depth" or "Vp" or "Vs") not in vmodel_data.columns:
        raise util.VelocityModelFileHeaderException

    return vmodel_data


class Run:
    """
    Light class to encapsulate i/o path information for a given run.

    Parameters
    ----------
    stage : str
        Specifies run stage of QuakeMigrate ("detect", "trigger", or "locate").
    path : str
        Points to the top level directory containing all input files, under
        which the specific run directory will be created.
    name : str
        Name of the current QuakeMigrate run.
    subname : str, optional
        Optional name of a sub-run - useful when testing different trigger
        parameters, for example.

    Attributes
    ----------
    path : `pathlib.Path` object
        Points to the top level directory containing all input files, under
        which the specific run directory will be created.
    name : str
        Name of the current QuakeMigrate run.
    run_path : `pathlib.Path` object
        Points to the run directory into which files will be written.
    subname : str
        Optional name of a sub-run - useful when testing different trigger
        parameters, for example.

    Methods
    -------
    logger(log)
        Spins up a logger configured to output to stdout or stdout + log file.

    """

    def __init__(self, path, name, subname="", stage=None):
        """Instantiate the Run object."""

        if "." in name or "." in subname:
            print("Warning: The character '.' is not allowed in run"
                  "names/subnames - replacing with '_'.")
            name = name.replace(".", "_")
            subname = subname.replace(".", "_")

        self.path = pathlib.Path(path) / name
        self._name = name
        self.stage = stage
        self.subname = subname

    def __str__(self):
        """Return short summary string of the Run object."""

        return (f"{util.log_spacer}\n{util.log_spacer}\n"
                f"\tQuakeMigrate RUN - Path: {self.path} - Name: {self.name}\n"
                f"{util.log_spacer}\n{util.log_spacer}\n")

    def logger(self, log):
        """
        Configures the logging feature.

        Parameters
        ----------
        log : bool
            Toggle for logging. If True, will output to stdout and generate a
            log file.

        """

        logstem = self.path / self.stage / self.subname / "logs" / self.name
        util.logger(logstem, log)
        logging.info(self)

    @property
    def name(self):
        """Get the run name as a formatted string."""
        if self.subname == "":
            return self._name
        else:
            return f"{self._name}_{self.subname}"
