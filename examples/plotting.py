from pytket.backends.backendresult import BackendResult
import matplotlib.pyplot as plt


def plot_qpe_results(result: BackendResult, n_strings: int = 4, dark_mode=False, y_limit=1000) -> None:
    """
    Plots results in a barchart given a BackendResult. the number of stings displayed
    can be specified with the n_strings argument.
    """
    counts_dict = result.get_counts()
    sorted_shots = counts_dict.most_common()

    n_most_common_strings = sorted_shots[:n_strings]
    x_axis_values = [str(entry[0]) for entry in n_most_common_strings]  # basis states
    y_axis_values = [entry[1] for entry in n_most_common_strings]  # counts

    if dark_mode:
        plt.style.use("dark_background")

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 0.75, 0.5])
    color_list = ["orange"] * (len(x_axis_values))
    ax.bar(
        x=x_axis_values,
        height=y_axis_values,
        color=color_list,
    )
    ax.set_title(label="Results")
    plt.ylim([0, y_limit])
    plt.xlabel("Basis State")
    plt.ylabel("Number of Shots")
    plt.xticks(rotation = 90) 
    plt.show()