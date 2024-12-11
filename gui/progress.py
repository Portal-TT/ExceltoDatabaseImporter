def update_status(message):
    global status_label
    if status_label:
        status_label.config(text=message)
