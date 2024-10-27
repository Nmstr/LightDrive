def clear_field(container: str, target_layout, *, amount_left: int = 1):
    """
    Clear a container of its contents
    :param container: The container to clear
    :param target_layout: The layout that should be added if none exists (e.g. QVboxLayout, QHboxLayout...)
    :param amount_left: The amount of elements that should be kept
    :return: None
    """
    # Check if the container has a layout, if not, set a new layout of type target_layout
    layout = container.layout()
    if layout is None:
        layout = target_layout
        container.setLayout(layout)

    while layout.count() > amount_left:
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
    return layout
