# caredx2024_rapid_prototyping

## Setup

This project implements a Multiple Traveling Salesmen Problem (MTSP) solver with a Gradio web interface.

## Features

- Solves the MTSP for 4 salesmen (staff members)
- Allows setting the number of users (5-50)
- Customizable depot location
- Ability to set forbidden users for each staff member
- Adjustable maximum cost for each staff member's route
- Visualizes the solution on a 2D plot

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install gradio numpy matplotlib ortools
   ```

## Usage

Run the application with:

```bash
python src/caredx2024_rapid_prototyping/app.py
```


Optional arguments:
- `--seed`: Set a random seed for reproducibility (default: 42)
- `--share`: Create a public link to share the interface

Example:
```bash
python src/caredx2024_rapid_prototyping/app.py --seed 42 --share
```


## Web Interface

The Gradio interface allows you to:

1. Set the number of users (5-50)
2. Choose the depot location (0-24)
3. Specify forbidden users for each staff member (comma-separated)
4. Set maximum cost for each staff member's route
5. Generate and visualize the MTSP solution

The solution is displayed as an image showing the routes for each staff member.

## Note

This is a prototype application and may have limitations in terms of scalability and optimization for large datasets.
