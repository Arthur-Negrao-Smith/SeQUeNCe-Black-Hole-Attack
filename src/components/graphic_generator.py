from .utils.enums import Colors

import numpy as np
import matplotlib.pyplot as plt

import logging

log: logging.Logger = logging.getLogger(__name__)


class Graphic_Gen:
    def __init__(self) -> None:
        self._x_axle: np.ndarray

        # dict[label] = (array, standar_deviation: True or False)
        self._y_axis: dict[str, tuple[np.ndarray, bool]]

        # dict[label] = array
        self._default_y_axis: dict[str, np.ndarray] | None = None

        self._plot_colors: dict[str, Colors] | None = None

    def define_x_axle(self, axle: np.ndarray) -> None:
        """
        Define x axle of the graphic

        Args:
            axle (numpy.ndarray[int]): Array 1D with each index is a x point
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
            axle (numpy.ndarray[numpy.ndarray]): Array 2D with each inner array is a point
            label (str): Label of axle
            standard_deviation (bool): If is True then standard deviation will plot with axle, else, don't show the standard deviation
            default_axle (numpy.ndarray[numpy.ndarray] | None): Array 2D with each inner array is a point to calculate the diference with axle y
            color (Colors | None): Color to add in current plot, if is None plot don't have a color
        """
        if color is not None:
            if self._plot_colors is None:
                self._plot_colors = dict()
            self._plot_colors[label] = color

            self._y_axis[label] = (axle, standard_deviation)

        if default_axle is not None:
            self._append_default_axle(default_axle, label=label)

    def _append_default_axle(self, axle: np.ndarray, label: str) -> None:
        """
        Append default axle to calculate the diference between y axle

        Args:
            axle (numpy.ndarray): Array 2D with each inner array is a point
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
        path_to_pdf: str | None = None,
    ) -> int:
        """
        Plot the graphic and show

        Args:
            tittle (str | None): Tittle of the graphic. If is None don't show graphic's tittle
            x_label (str | None): Label to show in x axle. If is None don't show a x label
            y_label (str | None): Label to show in y axle. If is None don't show a y label
            path_to_pdf (str | None): Path to save a PDF. If is None don't save a PDF

        Returns:
            int: Returns 0 if not error occurred. Return 1 if length of x axle is different of length of y axle. Return 2 if length of default axle is differet of the Y axle length
        """
        if len(self._x_axle) != len(self._y_axis):
            log.warning("X axle have a different length of the Y axle length")
            return 1

        if (self._default_y_axis is not None) and (
            len(self._y_axis) != len(self._default_y_axis)
        ):
            log.warning("Default axle have a different lenght of th Y axle length")
            return 2

        _, ax = plt.subplots()

        x_array_points: np.ndarray = self._x_axle

        # if is None avaliable colors is equal a []
        avaliable_colors: list[str] = (
            list(self._plot_colors.keys()) if self._plot_colors is not None else []
        )

        for label in self._y_axis.keys():

            current_y_tuple: tuple[np.ndarray, bool] = self._y_axis[label]

            # if default_y_axis exists
            if self._default_y_axis is not None:
                current_axle: np.ndarray = self._default_y_axis[label] - current_y_tuple
            else:
                current_axle: np.ndarray = current_y_tuple[0]

            mean: np.floating = np.mean(current_axle)
            std: np.floating = np.std(current_axle)

            # colors isn't None and color is a avaliable color
            if (self._plot_colors is not None) and (label in avaliable_colors):
                ax.plot(
                    mean,
                    label=label,
                    color=self._plot_colors[label].value,
                )
            # if don't have colors
            else:
                ax.plot(mean, label=label)

            # if axle have a standard deviation
            if current_y_tuple[1] == True:
                ax.fill_between(
                    x_array_points,
                    mean - std,
                    mean + std,
                )

        if tittle is not None:
            plt.title(tittle)

        if x_label is not None:
            plt.xlabel(x_label)

        if y_label is not None:
            plt.ylabel(y_label)

        plt.show()

        if path_to_pdf is not None:
            try:
                plt.savefig(path_to_pdf)
            except:
                log.warning(f"Error to save pdf in path: {path_to_pdf}")

        return 0
