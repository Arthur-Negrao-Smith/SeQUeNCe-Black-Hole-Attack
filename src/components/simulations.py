from concurrent.futures import ProcessPoolExecutor

from collections.abc import Callable
from typing import Any

class AsyncSimulator:
    """
    To create async simulations
    """
    def __init__(self, simulation_function: Callable[..., Any], runs: int, cores: int, need_id: bool = False) -> None:
        """
        Constructor for AsyncSimulator

        Args:
            simulation_function (Callable): Function with first parameter 'runs'
            runs (int): Total simulations rounds
            cores (int): Total cores to divide process. Don't use all cores of your machine
            need_id (bool): Flag to differentiate each process. To use this option the function should have a 'process_id' with second parameter
        """
        self.runs: int = runs
        self.cores: int = cores
        self.simulation_function: Callable[..., Any] = simulation_function
        self.need_id: bool = need_id

    def run(self, *args) -> list:
        """
        Run all simulations

        Args:
            *args (Any): All ordened args to simulations without 'runs' and 'process_id' parameter

        Returns:
            list: List with all data
        """
        runs_per_task: int = self.runs // self.cores
        module: int = self.runs % self.cores

        print(f"All simulations were divided in {self.cores} process")

        id: int = 0 # id to indentify process
        tasks: list = []
        with ProcessPoolExecutor(max_workers=self.cores) as executor:
            for task in range(0, self.cores):
                tmp_runs_per_task: int = runs_per_task
                if task < module and module > 0:
                    tmp_runs_per_task = runs_per_task + 1
                if self.need_id:
                    tasks.append(executor.submit(self.simulation_function, tmp_runs_per_task, id, *args))
                    id += 1
                else:
                    tasks.append(executor.submit(self.simulation_function, tmp_runs_per_task,*args))

        results: list = [task.result() for task in tasks]
        return results




