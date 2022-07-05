from optimizations import optimize_x_graph
from src.helpers.resources_monitor import measure_resources_usage

if __name__ == '__main__':
    # measure_resources_usage(lambda: optimize_lane_topology(600))
    measure_resources_usage(lambda: optimize_x_graph(max_optimisation_duration=600,
                                                     straight_non_straight_maneuver_penalty=120,
                                                     non_straight_straight_maneuver_penalty=0))
    # measure_resources_usage(lambda: optimize_normal(600))
