from concurrent.futures import ProcessPoolExecutor

from collections.abc import Callable
from typing import Any

class AsyncSimulator:
    """
    To create async simulations
    """
    def __init__(self, simulation_function: Callable[..., Any], runs: int, cores: int) -> None:
        """
        Constructor for AsyncSimulator

        Args:
            simulation_function (Callable): Function with first param 'runs'
            runs (int): Total simulations rounds
            cores (int): Total cores to divide process. Don't use all cores of your machine
        """
        self.runs: int = runs
        self.cores: int = cores
        self.simulation_function: Callable[..., Any] = simulation_function

    def run(self, *args) -> list:
        """
        Run all simulations

        Args:
            *args (Any): All ordened args to simulations without 'runs' parameter

        Returns:
            list: List with all data
        """
        runs_per_task: int = self.runs // self.cores
        module: int = self.runs % self.cores

        print(f"All simulations were divided in {self.cores} process")

        tasks: list = []
        with ProcessPoolExecutor(max_workers=self.cores) as executor:
            for task in range(0, self.cores):
                tmp_runs_per_task: int = runs_per_task
                if task < module and module > 0:
                    tmp_runs_per_task = runs_per_task + 1
                tasks.append(executor.submit(self.simulation_function, tmp_runs_per_task, *args))

        results: list = [task.result() for task in tasks]
        return results




