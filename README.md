# SeQUeNCe-Black-Hole-Attack

This repository focuses on quantum network attacks, especially to entanglement networks. Black Holes attacks can be a critical security vulnerability to exploit. Therefore, we are studying more about this kind of attack to understand its properties.

## Usage

To use this project initially, it is necessary to satisfy the [dependencies](#dependencies). After completing the dependencies step, clone this repository with following command:

```bash
git clone https://github.com/Arthur-Negrao-Smith/SeQUeNCe-Black-Hole-Attack.git
```

Change to the cloned repository:

```bash
cd SeQUeNCe-Black-Hole-Attack
```

Now, use Docker Compose to run any simulation with the following command:

```bash
docker compose -f compose/any_simulation_file.yaml up   # change the "any_simulation_file" to the any simulation file with a .yaml extension.

# example: docker compose -f compose/default_simulation.yaml up
```

If a _pip_ error occurs, just run the last command again until docker creates the image.

**Alert:** These simulations can be quite expensive and may take a long time to complete.

## Directories

```bash
.
├── compose/                        # files to use docker compose
├── src/                            # files to use simulations
│   ├── components/                 # directory with files to create simulations
│   │   └── utils/                  # utilities
│   ├── data/                       # directories to storage data
│   │   ├── default_simulation/     # directory to storage data from data_simulation.py
│   │   └── topology_simulation/    # directory to storage data from topology_simulation.py
│   └── examples/                   # directory to test features from sequence
├── tests/                          # directory to realize the tests with pytest
│   └── components/                 # directory to realize tests of src/components

```

## Hardware

- **CPU:** QEMU Virtual version 2.5+ (8)
- **GPU:** 00:02.0 Vendor 1234 Device 11
- **RAM:** 16 GB
- **STORAGE:** 50 GB
- **OS:** Ubuntu 22.04.5 LTS x86_64
- **KERNEL:** 5.15.0-143-generic
- **DOCKER:** 28.3.1 build 38b7060

## Dependencies

- [Docker](https://www.docker.com)
- [Docker Compose](https://docs.docker.com/compose/)

## Authors

- Arthur Negrão Smith  
- Diego Abreu  
- Antônio Jorge Gomes Abelém
