import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import argparse

def solve_mtsp(n_users, depot, forbidden_users_1, forbidden_users_2, forbidden_users_3, forbidden_users_4, max_cost_1, max_cost_2, max_cost_3, max_cost_4):
    n_salesmen = 4  # Fixed number of salesmen
    
    # Parse forbidden users
    forbidden_users = [
        list(map(int, forbidden_users_1.split(','))),
        list(map(int, forbidden_users_2.split(','))),
        list(map(int, forbidden_users_3.split(','))),
        list(map(int, forbidden_users_4.split(','))),
    ]
    
    # Create max_costs list
    max_costs = [max_cost_1, max_cost_2, max_cost_3, max_cost_4]
    users = np.random.rand(n_users, 2) * 100

    # Calculate distance matrix
    dist = np.sqrt(((users[:, None, :] - users[None, :, :]) ** 2).sum(axis=2))

    # Create data model
    data = {
        'distance_matrix': dist.astype(int),
        'num_vehicles': n_salesmen,
        'depot': depot
    }

    # Create routing index manager and model
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    # Define distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add distance dimension
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)

    # Add maximum cost constraints
    for vehicle_id, max_cost in enumerate(max_costs):
        index = routing.End(vehicle_id)
        distance_dimension.SetCumulVarSoftUpperBound(index, max_cost, 1000)

    # Add forbidden users constraints
    for vehicle_id, f_users in enumerate(forbidden_users):
        for user in f_users:
            if user != depot and user < n_users:
                routing.VehicleVar(manager.NodeToIndex(user)).RemoveValue(vehicle_id)

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(10)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # Extract routes
        routes = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = [manager.IndexToNode(index)]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
            routes.append(route)

        # Visualize solution
        plt.figure(figsize=(10, 10))
        plt.scatter(users[:, 0], users[:, 1], c='red', s=50)
        for i, user in enumerate(users):
            plt.annotate(f'user {i}', (user[0], user[1]), xytext=(5, 5), textcoords='offset points')

        colors = ['b', 'g', 'c', 'm']
        for k, route in enumerate(routes):
            route_coords = users[route]
            plt.plot(route_coords[:, 0], route_coords[:, 1], c=colors[k], linewidth=2, label=f'staff {k+1}')
            for i in range(len(route) - 1):
                plt.annotate('', xy=users[route[i+1]], xytext=users[route[i]],
                             arrowprops=dict(arrowstyle='->', color=colors[k], lw=1.5))

        plt.title('Human Care Crew Scheduling Problem Solution')
        plt.legend()
        plt.grid(True)
        
        # Save the plot to a file
        plt.savefig('mtsp_solution.png')
        plt.close()

        return 'mtsp_solution.png'
    else:
        return "No solution found!"

def main(seed, share):
    # Set the random seed
    np.random.seed(seed)

    # Define Gradio interface
    iface = gr.Interface(
        fn=solve_mtsp,
        inputs=[
            gr.Slider(minimum=5, maximum=50, step=1, label="Number of users", value=25),
            gr.Slider(minimum=0, maximum=24, step=1, label="Depot Location", value=0),
            gr.Textbox(label="Forbidden users for staff 1 (comma-separated)", value="2,3"),
            gr.Textbox(label="Forbidden users for staff 2 (comma-separated)", value="4,5"),
            gr.Textbox(label="Forbidden users for staff 3 (comma-separated)", value="6,7"),
            gr.Textbox(label="Forbidden users for staff 4 (comma-separated)", value="8,9"),
            gr.Slider(minimum=100, maximum=500, step=10, label="Max Cost for staff 1", value=200),
            gr.Slider(minimum=100, maximum=500, step=10, label="Max Cost for staff 2", value=200),
            gr.Slider(minimum=100, maximum=500, step=10, label="Max Cost for staff 3", value=200),
            gr.Slider(minimum=100, maximum=500, step=10, label="Max Cost for staff 4", value=200),
        ],
        outputs=gr.Image(type="filepath", label="MTSP Solution"),
        title="Multiple Traveling Salesmen Problem Solver",
        description="Enter the number of users, depot location, forbidden users for each staff, and maximum costs.",
    )

    # Launch the app
    iface.launch(share=share)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MTSP Solver with Gradio Interface")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--share", action="store_true", help="Whether to create a public link")
    args = parser.parse_args()

    main(args.seed, args.share)