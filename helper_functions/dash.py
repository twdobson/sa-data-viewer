def get_callback_trigger(callback_context):
    """Returns the element which triggered a callback

    Args:
        callback_context (dash._callback_context.CallbackContext): callback context

    Returns:
        string: name of element which triggered the callback
    """
    if not callback_context.triggered:
        trigger_id = None
    else:
        trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    return trigger_id
