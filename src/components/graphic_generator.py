from .utils.enums import Colors

import numpy as np
import matplotlib.pyplot as plt

import logging

log: logging.Logger = logging.getLogger(__name__)


class Graphic_Gen:
    def __init__(self) -> None:
        self._x_axle: np.ndarray

        # dict[label] = (array, standar_deviation: True or False)
        self._y_axis: dict[str, tuple[np.ndarray, bool]] = dict()

        # dict[label] = array
        self._default_y_axis: dict[str, np.ndarray] | None = None

        self._plot_colors: dict[str, Colors] | None = None

    def define_x_axle(self, axle: np.ndarray) -> None:
        """
        Define x axle of the graphic

        Args:
            axle (ndarray[int]): Array 1D with each index is a x point
        """
        self._x_axle = axle

    def append_y_axle(
        self,
        axle: np.ndarray,
        label: str,
        standard_deviation: bool = False,
        default_axle: np.ndarray | None = None,
        color: Colors | None = None,
    ) -> None:
        """
        Append y axle into the graph

        Args:
            axle (ndarray[ndarray]): Array 2D with each inner array is a point
            label (str): Label of axle
            standard_deviation (bool): If is True then standard deviation will plot with axle, else, don't show the standard deviation
            default_axle (ndarray[ndarray] | None): 2D array to subtract `axle`. All arrays are trimmed to the shortest length if `axle` is given. If is None just plot `axle`
            color (Colors | None): Color to add in current plot, if is None plot don't have a color
        """
        if color is not None:
            if self._plot_colors is None:
                self._plot_colors = dict()
            self._plot_colors[label] = color

        y_axle: np.ndarray = axle

        # if have a default_axle
        if default_axle is not None:

            # find the min length
            axle_min_length: int = min([len(array) for array in y_axle])
            default_axle_length: int = min([len(array) for array in default_axle])
            min_length: int = min(axle_min_length, default_axle_length)

            # slice the arrays
            y_axle = np.array([array[:min_length] for array in y_axle])
            default_axle = np.array(default_axle[:min_length])

            self._append_default_axle(default_axle, label=label)

        self._y_axis[label] = (y_axle, standard_deviation)

    def _append_default_axle(self, axle: np.ndarray, label: str) -> None:
        """
        Append default axle to calculate the diference between y axle

        Args:
            axle (ndarray[ndarray]): Array 2D with each inner array is a point
            label (str): Label of axle
        """
        if self._default_y_axis is None:
            self._default_y_axis = {}

        self._default_y_axis[label] = axle

    def plot(
        self,
        tittle: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        grid: bool = False,
        marker: str = ".",
        path_to_pdf: str | None = None,
    ) -> int:
        """
        Plot the graphic and show

        Args:
            tittle (str | None): Tittle of the graphic. If is None don't show graphic's tittle
            x_label (str | None): Label to show in x axle. If is None don't show a x label
            y_label (str | None): Label to show in y axle. If is None don't show a y label
            grid (bool): If is True show the grid in graphic, else, don't show
            marker (str): Marker to show each point
            path_to_pdf (str | None): Path to save a PDF. If is None don't save a PDF

        Returns:
            int: Returns 0 if not error occurred. Return 1 if length of x axle is different of length of y axle.
        """

        # if is None avaliable colors is equal a []
        avaliable_colors: list[str] = (
            list(self._plot_colors.keys()) if self._plot_colors is not None else []
        )

        for label in self._y_axis.keys():

            # if exists default y axis
            if self._default_y_axis is not None:
                y_points: np.ndarray = (
                    self._default_y_axis[label] - self._y_axis[label][0]
                )
            else:
                y_points: np.ndarray = self._y_axis[label][0]

            # convert 2D array in 1D array
            y_mean_array = np.mean(y_points, axis=1)
            y_std_array = np.std(y_points, axis=1)

            # if x and y have different points number
            if len(self._x_axle) != len(y_mean_array):
                log.warning("X axle have a different length of the Y axle length")
                return 1

            # colors isn't None and color is a avaliable color
            if (self._plot_colors is not None) and (label in avaliable_colors):
                color: str | None = self._plot_colors[label].value
            # if don't have colors
            else:
                color = None

            # if axle have a standard deviation
            if self._y_axis[label][1] == True:
                plt.errorbar(
                    self._x_axle,
                    y_mean_array,
                    yerr=y_std_array,
                    label=label,
                    marker=marker,
                    color=color,
                )
            else:
                plt.plot(
                    self._x_axle, y_mean_array, label=label, marker=marker, color=color
                )

        if tittle is not None:
            plt.title(tittle)

        if x_label is not None:
            plt.xlabel(x_label)

        if y_label is not None:
            plt.ylabel(y_label)

        if grid:
            plt.grid(True, linestyle="--", color="gray", alpha=0.5)

        plt.legend()
        plt.show()

        if path_to_pdf is not None:
            try:
                plt.savefig(path_to_pdf)
            except:
                log.warning(f"Error to save pdf in path: {path_to_pdf}")

        return 0
