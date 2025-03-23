import tkinter as tk
from tkinter import ttk, filedialog
import json

# Dictionary to store counts
counts = {f"Cell {i}": 0 for i in range(1, 21)}
counts["Lycopodium"] = 0  # Add Lycopodium to the counts dictionary

# Default key bindings
key_mapping = {
    "q": "Cell 1", "w": "Cell 2",
    "e": "Cell 3", "r": "Cell 4",
    "t": "Cell 5", "a": "Cell 6",
    "s": "Cell 7", "d": "Cell 8",
    "f": "Cell 9", "g": "Cell 10",
    "z": "Cell 11", "x": "Cell 12",
    "c": "Cell 13", "v": "Cell 14",
    "b": "Cell 15", "y": "Cell 16", "u": "Cell 17",
    "i": "Cell 18", "o": "Cell 19", "p": "Cell 20",
    "space": "Lycopodium"  # Space bar for Lycopodium
}

# Update label text with renamed categories
def update_labels():

    for key, label in list(labels.items()):  # Ensure safe iteration
        # 🔥 Fix: If `key` was renamed, update reference
        if key in renamed_categories:
            key = renamed_categories[key]

        if key not in counts:
            print(f"Error: Missing key in counts -> {key}")  # Debug missing key
            continue  # Skip instead of adding back the missing key

        label.config(text=str(counts[key]))

    for i, category in enumerate(categories):
        if i < len(label_widgets):
            display_name = renamed_categories.get(category, category)
            label_widgets[i].config(text=display_name)

# Function to add count
def add_count(category, key=None):
    counts[category] += 1
    update_labels()
    update_sum()
    if key:
        keystroke_log.insert(tk.END, f"+1 {category} -> {key}\n")
    else:
        keystroke_log.insert(tk.END, f"+1 {category}\n")
    keystroke_log.yview(tk.END)

# Function to subtract count
def subtract_count(category):
    if counts[category] > 0:
        counts[category] -= 1
        update_labels()
        update_sum()
        keystroke_log.insert(tk.END, f"-1 {category}\n")
        keystroke_log.yview(tk.END)

# Function to reset counts
def reset_counts():
    for key in counts:
        counts[key] = 0
    update_labels()
    update_sum()
    keystroke_log.delete(1.0, tk.END)

# Function to update the total sum
def update_sum():
    total = sum(count for category, count in counts.items() if category != "Lycopodium")
    sum_label.config(text=f"Total (excl. Lycopodium): {total}")

# Function to handle key presses
def key_press(event):
    if notebook.index(notebook.select()) == 0:  # Only in the "Counter" tab
        key = event.keysym.lower()
        if key in key_mapping:
            category = key_mapping[key]
            # 🔥 FIX: Resolve the correct category name using renamed_categories
            resolved_category = renamed_categories.get(category, category)
            if resolved_category in counts:  # Check if the resolved category exists in counts
                add_count(resolved_category, key)
            else:
                print(f"Error: Resolved category '{resolved_category}' not found in counts.")


# Function to update the key mappings frame
def update_key_mappings_frame():
    for widget in key_mappings_frame.winfo_children():
        widget.destroy()
    for i, (key, value) in enumerate(key_mapping.items()):
        row = i // 4
        col = i % 4
        label = tk.Label(key_mappings_frame, text=f"{value} -> {key.upper()}", font=("Arial", 6), width=16, anchor="w")
        label.grid(row=row, column=col, padx=5, pady=2, sticky="E")


# Function to apply custom labels
def apply_custom_labels(event=None):
    global renamed_categories

    warning_label_custom_labels.config(text="", fg="black")

    new_categories = []
    for old_category, entry in entry_widgets.items():
        new_category = entry.get().strip()
        if not new_category:
            continue
        if new_category in new_categories:
            warning_label_custom_labels.config(text="Error: Duplicate label names are not allowed.", fg="red")
            return
        new_categories.append(new_category)

    for old_category, entry in entry_widgets.items():
        new_category = entry.get().strip()
        if old_category in renamed_categories:
            old_category = renamed_categories[old_category]

        if old_category in counts:
            if new_category and new_category != old_category:
                if new_category in counts:
                    warning_label_custom_labels.config(text="Error: Duplicate label names are not allowed.", fg="red")
                    return  

                counts[new_category] = counts.pop(old_category)

                if old_category in labels:
                    labels[new_category] = labels.pop(old_category)
                    labels[new_category].config(text=str(counts[new_category]))

                if old_category in categories:
                    index = categories.index(old_category)
                    categories[index] = new_category

                # 🔥 FIX: Update key_mapping to use the new category name
                for key, value in list(key_mapping.items()):
                    if value == old_category:
                        key_mapping[key] = new_category

                if index < len(label_widgets):
                    label_widgets[index].config(text=new_category)

                if index < len(add_buttons):
                    add_buttons[index].config(command=lambda c=new_category: add_count(c))
                if index < len(subtract_buttons):
                    subtract_buttons[index].config(command=lambda c=new_category: subtract_count(c))

                if old_category in key_entry_widgets:
                    key_entry_widgets[new_category] = key_entry_widgets.pop(old_category)

                renamed_categories[old_category] = new_category

    update_labels()
    update_sum()
    update_key_mappings_frame()
    update_key_config_display()


# Function to update the key configuration display
def update_key_config_display():
    # Clear existing widgets
    for widget in config_keys_content_frame.winfo_children():
        widget.destroy()

    # Split categories into two groups for two columns
    first_column_categories = categories[:10]  # First 10 categories
    second_column_categories = categories[10:]  # Remaining categories

    # Add labels and key entry fields for the first column
    for i, category in enumerate(first_column_categories):
        display_name = renamed_categories.get(category, category)  # Get renamed category
        # Label (e.g., "Label 1", "Label 2", etc.)
        label = tk.Label(config_keys_content_frame, text=f"{display_name}:", font=("Arial", 10), anchor="w")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        # Key entry field
        key_entry = tk.Entry(config_keys_content_frame, width=10)
        key_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")

        # Populate the key entry field with the current key binding
        for key, value in key_mapping.items():
            if value == category:
                key_entry.insert(0, key.upper())
                break

        # Store the entry widget for later use
        key_entry_widgets[category] = key_entry

        # Bind the <FocusOut> and <Return> events to apply_key_bindings
        key_entry.bind("<FocusOut>", lambda event, c=category: apply_key_bindings())
        key_entry.bind("<Return>", lambda event, c=category: apply_key_bindings())

    # Add labels and key entry fields for the second column
    for i, category in enumerate(second_column_categories):
        display_name = renamed_categories.get(category, category)  # Get renamed category
        # Label (e.g., "Label 11", "Label 12", etc.)
        label = tk.Label(config_keys_content_frame, text=f"{display_name}:", font=("Arial", 10), anchor="w")
        label.grid(row=i, column=2, padx=10, pady=5, sticky="w")

        # Key entry field
        key_entry = tk.Entry(config_keys_content_frame, width=10)
        key_entry.grid(row=i, column=3, padx=10, pady=5, sticky="w")

        # Populate the key entry field with the current key binding
        for key, value in key_mapping.items():
            if value == category:
                key_entry.insert(0, key.upper())
                break

        # Store the entry widget for later use
        key_entry_widgets[category] = key_entry

        # Bind the <FocusOut> and <Return> events to apply_key_bindings
        key_entry.bind("<FocusOut>", lambda event, c=category: apply_key_bindings())
        key_entry.bind("<Return>", lambda event, c=category: apply_key_bindings())

    # Add a button to apply key changes
    btn_apply_keys = tk.Button(config_keys_content_frame, text="Apply Key Bindings", command=apply_key_bindings, width=20, height=2)
    btn_apply_keys.grid(row=max(len(first_column_categories), len(second_column_categories)), column=0, columnspan=4, pady=10)

    # Add a warning label to the Configure Keys tab
    global warning_label_config_keys
    warning_label_config_keys = tk.Label(config_keys_content_frame, text="", fg="red", font=("Arial", 10))
    warning_label_config_keys.grid(row=max(len(first_column_categories), len(second_column_categories)) + 1, column=0, columnspan=4, pady=10)


# Function to apply key bindings
def apply_key_bindings():
    # Clear any previous warning
    if warning_label_config_keys.winfo_exists():
        warning_label_config_keys.config(text="", fg="black")

    # Track new key bindings to detect duplicates
    new_keys = []

    for category, entry in key_entry_widgets.items():
        if entry.winfo_exists():
            try:
                key = entry.get().strip().lower()  # Remove leading/trailing spaces and convert to lowercase
                if key:
                    # Check for duplicates
                    if key in new_keys:
                        if warning_label_config_keys.winfo_exists():
                            warning_label_config_keys.config(text="Error: Duplicate key bindings are not allowed.", fg="red")
                        return  # Stop further processing

                    # Check if the key is already mapped to another category
                    if key in key_mapping and key_mapping[key] != category:
                        if warning_label_config_keys.winfo_exists():
                            warning_label_config_keys.config(text="Error: Duplicate key bindings are not allowed.", fg="red")
                        return  # Stop further processing

                    new_keys.append(key)

                    # Remove the old key binding (if any)
                    for k, v in list(key_mapping.items()):
                        if v == category:
                            del key_mapping[k]
                    # Assign the new key binding
                    key_mapping[key] = category
            except _tkinter.TclError as e:
                print(f"Error accessing entry widget for category '{category}': {e}")
        else:
            print(f"Entry widget for category '{category}' does not exist!")

    # Refresh the UI
    update_key_mappings_frame()


# Function to exit the application
def exit_app():
    root.quit()

# Creating the main window
root = tk.Tk()
root.bind("<KeyPress>", key_press)
root.title("Pollen Grain Counter v.1.0")
root.geometry("820x640")

# Configure the root window to make rows and columns resizable
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a custom style for the notebook tabs
style = ttk.Style()
style.configure("TNotebook.Tab", padding=[10, 5], font=("Arial", 10), background="lightgray")
style.map("TNotebook.Tab", background=[("selected", "white")], relief=[("selected", "raised")])

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# Create frames for each tab
counter_frame = ttk.Frame(notebook)
custom_labels_frame = ttk.Frame(notebook)
config_keys_frame = ttk.Frame(notebook)

# Add frames to the notebook
notebook.add(counter_frame, text="Counter")
notebook.add(custom_labels_frame, text="Custom Labels")
notebook.add(config_keys_frame, text="Configure Keys")

# Make the notebook expand to fill the window
notebook.grid_rowconfigure(0, weight=1)
notebook.grid_columnconfigure(0, weight=1)

# Function to create a scrollable frame
def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    return frame

# Counter Tab
counter_scrollable_frame = create_scrollable_frame(counter_frame)

# Creating buttons and labels
labels = {}
label_widgets = []  # List to store label widgets for updating
add_buttons = []     # List to store add buttons
subtract_buttons = [] # List to store subtract buttons

# Categories (generic names)
categories = [f"Cell {i}" for i in range(1, 21)] + ["Lycopodium"]  # Include Lycopodium in categories

# Split categories into two groups
first_column_categories = categories[:10]
second_column_categories = categories[10:20]  # Exclude Lycopodium from the second column

# First column
for i, category in enumerate(first_column_categories):
    # Category label
    label = tk.Label(counter_scrollable_frame, text=category, font=("Arial", 12), width=15, anchor="w")
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    label_widgets.append(label)
    
    # Count label
    count_label = tk.Label(counter_scrollable_frame, text="0", font=("Arial", 12), width=10)
    count_label.grid(row=i, column=0, padx=10, pady=5, sticky="E")
    labels[category] = count_label
    
    # Add button
    btn_add = tk.Button(counter_scrollable_frame, text="+", command=lambda c=category: add_count(c), width=5, height=1)
    btn_add.grid(row=i, column=1, padx=5, pady=5, sticky="W")
    add_buttons.append(btn_add)
    
    # Subtract button
    btn_subtract = tk.Button(counter_scrollable_frame, text="-", command=lambda c=category: subtract_count(c), width=5, height=1)
    btn_subtract.grid(row=i, column=1, padx=5, pady=5)
    subtract_buttons.append(btn_subtract)

# Second column
for i, category in enumerate(second_column_categories):
    # Category label
    label = tk.Label(counter_scrollable_frame, text=category, font=("Arial", 12), width=15, anchor="w")
    label.grid(row=i, column=2, padx=10, pady=5, sticky="E")
    label_widgets.append(label)
    
    # Count label
    count_label = tk.Label(counter_scrollable_frame, text="0", font=("Arial", 12), width=10, anchor="w")
    btn_add.grid_columnconfigure(4, weight = 0)
    count_label.grid(row=i, column=3, padx=10, pady=5, sticky = tk.W)
    labels[category] = count_label
    
    # Add button
    btn_add = tk.Button(counter_scrollable_frame, text="+", command=lambda c=category: add_count(c), width=5, height=1)
    btn_add.grid(row=i, column=3, padx=5, pady=5, sticky="E")
    add_buttons.append(btn_add)
    
    # Subtract button
    btn_subtract = tk.Button(counter_scrollable_frame, text="-", command=lambda c=category: subtract_count(c), width=5, height=1)
    btn_subtract.grid(row=i, column=4, padx=5, pady=5, sticky="W")
    subtract_buttons.append(btn_subtract)

# Lycopodium button (placed just below the cell buttons)
lycopodium_label = tk.Label(counter_scrollable_frame, text="Lycopodium", font=("Arial", 12, "bold"), width=15, anchor="w")
lycopodium_label.grid(row=len(first_column_categories), column=2, padx=10, pady=5, sticky="w")
label_widgets.append(lycopodium_label)

lycopodium_count = tk.Label(counter_scrollable_frame, text="0", font=("Arial", 12, "bold"), width=10, anchor="w")
lycopodium_count.grid(row=len(first_column_categories), column=3, padx=10, pady=5,  sticky="w")
labels["Lycopodium"] = lycopodium_count

lycopodium_add = tk.Button(counter_scrollable_frame, text="+", command=lambda: add_count("Lycopodium"), width=5, height=1)
lycopodium_add.grid(row=len(first_column_categories), column=3, padx=5, pady=5, sticky="E")
add_buttons.append(lycopodium_add)

lycopodium_subtract = tk.Button(counter_scrollable_frame, text="-", command=lambda: subtract_count("Lycopodium"), width=5, height=1)
lycopodium_subtract.grid(row=len(first_column_categories), column=4, padx=5, pady=5, sticky="W")
subtract_buttons.append(lycopodium_subtract)


# Creating the key_mappings_frame with square border and small size
key_mappings_frame = tk.Frame(counter_scrollable_frame, bd=1, relief="solid", width=100)
key_mappings_frame.grid(row=11, column=0, rowspan=6, columnspan=2, padx=20, pady=10, sticky="W")


# Update the key mappings frame initially
update_key_mappings_frame()


# Create sum label at the bottom (centered)
sum_label = tk.Label(counter_scrollable_frame, text="Total (excl. Lycopodium): 0", font=("Arial", 11, "bold"), anchor="center")
sum_label.grid(row=6, column=0, rowspan=6, columnspan=2, padx=20, pady=10, sticky="W")


# Keystroke log
keystroke_log = tk.Text(counter_scrollable_frame, height=7, width=41)
keystroke_log.grid(row=11, column=2, columnspan=6, pady=10)



# Control buttons (moved down by 1 row)
btn_reset = tk.Button(counter_scrollable_frame, text="Reset", command=reset_counts, width=15, height=2)
btn_reset.grid(row=len(categories) + 2, column=0, pady=10)

btn_exit = tk.Button(counter_scrollable_frame, text="Exit", command=exit_app, width=15, height=2)
btn_exit.grid(row=len(categories) + 2, column=3, pady=10)



# Custom Labels Tab
custom_labels_scrollable_frame = create_scrollable_frame(custom_labels_frame)


# Create a frame to hold the labels and entry fields
custom_labels_content_frame = tk.Frame(custom_labels_scrollable_frame)
custom_labels_content_frame.pack(pady=20)  # Add vertical padding


# Dictionary to track renaming history
renamed_categories = {}

# Function to apply custom labels
def apply_custom_labels(event=None):  # Add event=None to handle event binding
    global renamed_categories

    # Clear any previous warning
    warning_label_custom_labels.config(text="", fg="black")

    # Track new category names to detect duplicates
    new_categories = []

    for old_category, entry in entry_widgets.items():
        new_category = entry.get().strip()  # Remove leading/trailing spaces

        # Skip empty entries
        if not new_category:
            continue

        # Check for duplicates
        if new_category in new_categories:
            warning_label_custom_labels.config(text="Error: Duplicate label names are not allowed.", fg="red")
            return  # Stop further processing

        new_categories.append(new_category)

    # If no duplicates, proceed with renaming
    for old_category, entry in entry_widgets.items():
        new_category = entry.get().strip()

        # If old_category is in renamed_categories, replace it with the latest name
        if old_category in renamed_categories:
            old_category = renamed_categories[old_category]

        # Ensure old_category exists in counts before renaming
        if old_category in counts:
            if new_category and new_category != old_category:
                # Check if the new category already exists in counts
                if new_category in counts:
                    warning_label_custom_labels.config(text="Error: Duplicate label names are not allowed.", fg="red")
                    return  # Stop further processing

                # Move data to new category
                counts[new_category] = counts.pop(old_category)

                # Update labels dictionary
                if old_category in labels:
                    labels[new_category] = labels.pop(old_category)
                    labels[new_category].config(text=str(counts[new_category]))

                # Update categories list
                if old_category in categories:
                    index = categories.index(old_category)
                    categories[index] = new_category

                # Update key mapping
                for key, value in list(key_mapping.items()):
                    if value == old_category:
                        key_mapping[key] = new_category

                # Update displayed label text
                if index < len(label_widgets):
                    label_widgets[index].config(text=new_category)

                # Update button commands
                if index < len(add_buttons):
                    add_buttons[index].config(command=lambda c=new_category: add_count(c))
                if index < len(subtract_buttons):
                    subtract_buttons[index].config(command=lambda c=new_category: subtract_count(c))

                # Update key_entry_widgets dictionary
                if old_category in key_entry_widgets:
                    key_entry_widgets[new_category] = key_entry_widgets.pop(old_category)

                # Store renaming history
                renamed_categories[old_category] = new_category
        else:
            # If the category doesn't exist in counts, ensure we aren't repeatedly warning
            if old_category not in renamed_categories and old_category not in counts:
                print(f"Warning: '{old_category}' not found in counts. It may have already been renamed.")

    # Refresh the UI
    update_labels()  # Ensure this updates labels correctly
    update_sum()
    update_key_mappings_frame()
    update_key_config_display()



entry_widgets = {}

# First column for Labels 1-10
for i, category in enumerate(categories[:10]):
    # Label (e.g., "Label 1", "Label 2", etc.)
    label = tk.Label(custom_labels_content_frame, text=f"Label {i + 1}:", font=("Arial", 10), anchor="w")
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

    # Entry field
    entry = tk.Entry(custom_labels_content_frame, width=20)
    entry.insert(0, category)
    entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
    entry_widgets[category] = entry

    # Bind the <FocusOut> and <Return> events to apply_custom_labels
    entry.bind("<FocusOut>", lambda event: apply_custom_labels())
    entry.bind("<Return>", lambda event: apply_custom_labels())

# Second column for Labels 11-20 + Lycopodium
for i, category in enumerate(categories[10:]):
    # Label (e.g., "Label 11", "Label 12", etc.)
    label = tk.Label(custom_labels_content_frame, text=f"Label {i + 11}:", font=("Arial", 10), anchor="w")
    label.grid(row=i, column=2, padx=10, pady=5, sticky="w")

    # Entry field
    entry = tk.Entry(custom_labels_content_frame, width=20)
    entry.insert(0, category)
    entry.grid(row=i, column=3, padx=10, pady=5, sticky="w")
    entry_widgets[category] = entry

    # Bind the <FocusOut> and <Return> events to apply_custom_labels
    entry.bind("<FocusOut>", lambda event: apply_custom_labels())
    entry.bind("<Return>", lambda event: apply_custom_labels())




# Configure Keys Tab
config_keys_scrollable_frame = create_scrollable_frame(config_keys_frame)

# Create a frame to hold the labels and key entry fields
config_keys_content_frame = tk.Frame(config_keys_scrollable_frame)
config_keys_content_frame.pack(pady=20)  # Add vertical padding




# Add thin vertical division between the two columns
vertical_divider = tk.Frame(counter_scrollable_frame, bd=0.5, relief="sunken", width=1, bg="gray88")
vertical_divider.grid(row=0, column=0, columnspan=10, rowspan=10, sticky="ew")

# Add thin vertical division between the two columns
vertical_divider = tk.Frame(counter_scrollable_frame, bd=0.5, relief="sunken", width=1, bg="gray88")
vertical_divider.grid(row=5, column=0, columnspan=10, rowspan=10, sticky="ew")


# Add thin horizontal division between Cell 5 and Cell 6

horizontal_divider = tk.Frame(counter_scrollable_frame, bd=0.5, relief="sunken", height=1, bg="gray88")
horizontal_divider.grid(row=0, column=0, columnspan=10, rowspan=10, sticky="ns")



# Add a warning label to the Custom Labels tab
warning_label_custom_labels = tk.Label(custom_labels_content_frame, text="", fg="red", font=("Arial", 10))
warning_label_custom_labels.grid(row=len(categories) + 1, column=0, columnspan=4, pady=10)

# Add a warning label to the Configure Keys tab
warning_label_config_keys = tk.Label(config_keys_content_frame, text="", fg="red", font=("Arial", 10))
warning_label_config_keys.grid(row=max(len(categories[:10]), len(categories[10:])) + 1, column=0, columnspan=4, pady=10)

# Dictionary to store key entry widgets
key_entry_widgets = {}

# Function to update the key configuration display
def update_key_config_display():
    # Clear existing widgets
    for widget in config_keys_content_frame.winfo_children():
        widget.destroy()

    # Split categories into two groups for two columns
    first_column_categories = categories[:10]  # First 10 categories
    second_column_categories = categories[10:]  # Remaining categories

    # Add labels and key entry fields for the first column
    for i, category in enumerate(first_column_categories):
        display_name = renamed_categories.get(category, category)  # Get renamed category
        # Label (e.g., "Label 1", "Label 2", etc.)
        label = tk.Label(config_keys_content_frame, text=f"{display_name}:", font=("Arial", 10), anchor="w")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        # Key entry field
        key_entry = tk.Entry(config_keys_content_frame, width=10)
        key_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")

        # Populate the key entry field with the current key binding
        for key, value in key_mapping.items():
            if value == category:
                key_entry.insert(0, key.upper())
                break

        # Store the entry widget for later use
        key_entry_widgets[category] = key_entry

        # Bind the <FocusOut> and <Return> events to apply_key_bindings
        key_entry.bind("<FocusOut>", lambda event, c=category: apply_key_bindings())
        key_entry.bind("<Return>", lambda event, c=category: apply_key_bindings())

    # Add labels and key entry fields for the second column
    for i, category in enumerate(second_column_categories):
        display_name = renamed_categories.get(category, category)  # Get renamed category
        # Label (e.g., "Label 11", "Label 12", etc.)
        label = tk.Label(config_keys_content_frame, text=f"{display_name}:", font=("Arial", 10), anchor="w")
        label.grid(row=i, column=2, padx=10, pady=5, sticky="w")

        # Key entry field
        key_entry = tk.Entry(config_keys_content_frame, width=10)
        key_entry.grid(row=i, column=3, padx=10, pady=5, sticky="w")

        # Populate the key entry field with the current key binding
        for key, value in key_mapping.items():
            if value == category:
                key_entry.insert(0, key.upper())
                break

        # Store the entry widget for later use
        key_entry_widgets[category] = key_entry

        # Bind the <FocusOut> and <Return> events to apply_key_bindings
        key_entry.bind("<FocusOut>", lambda event, c=category: apply_key_bindings())
        key_entry.bind("<Return>", lambda event, c=category: apply_key_bindings())

    # Add a button to apply key changes
    btn_apply_keys = tk.Button(config_keys_content_frame, text="Apply Key Bindings", command=apply_key_bindings, width=20, height=2)
    btn_apply_keys.grid(row=max(len(first_column_categories), len(second_column_categories)), column=0, columnspan=4, pady=10)

    # Add a warning label to the Configure Keys tab
    global warning_label_config_keys
    warning_label_config_keys = tk.Label(config_keys_content_frame, text="", fg="red", font=("Arial", 10))
    warning_label_config_keys.grid(row=max(len(first_column_categories), len(second_column_categories)) + 1, column=0, columnspan=4, pady=10)


# Function to apply key bindings
def apply_key_bindings():
    # Clear any previous warning
    if warning_label_config_keys.winfo_exists():
        warning_label_config_keys.config(text="", fg="black")

    # Track new key bindings to detect duplicates
    new_keys = []

    for category, entry in key_entry_widgets.items():
        if entry.winfo_exists():
            try:
                key = entry.get().strip().lower()  # Remove leading/trailing spaces and convert to lowercase
                if key:
                    # Check for duplicates
                    if key in new_keys:
                        if warning_label_config_keys.winfo_exists():
                            warning_label_config_keys.config(text="Error: Duplicate key bindings are not allowed.", fg="red")
                        return  # Stop further processing

                    # Check if the key is already mapped to another category
                    if key in key_mapping and key_mapping[key] != category:
                        if warning_label_config_keys.winfo_exists():
                            warning_label_config_keys.config(text="Error: Duplicate key bindings are not allowed.", fg="red")
                        return  # Stop further processing

                    new_keys.append(key)

                    # Remove the old key binding (if any)
                    for k, v in list(key_mapping.items()):
                        if v == category:
                            del key_mapping[k]
                    # Assign the new key binding
                    key_mapping[key] = category
            except _tkinter.TclError as e:
                print(f"Error accessing entry widget for category '{category}': {e}")
        else:
            print(f"Entry widget for category '{category}' does not exist!")

    # Refresh the UI
    update_key_mappings_frame()
# Initialize the key configuration display
update_key_config_display()


#####################

# Create a new Help tab
help_frame = ttk.Frame(notebook)
notebook.add(help_frame, text="Help")

# Add a Label or Text widget to display help content
help_text = """
Welcome to the Pollen Grain Counter!

This application allows you to count pollen grains for various categories.
(Other things are allowed to be counted as well, at the user's discretion)


You can use the following features:

1. **Counter Tab**: Use this tab to increment and decrement counts for various categories.
2. **Custom Labels Tab**: Rename categories to match your specific needs.
3. **Configure Keys Tab**: Change the key bindings for each category.

Key Bindings by default:
- q, w, e, r, t, a, s, d, f, g, z, x, c, v, b, y, u, i, o, p: Increment counts for corresponding cells.
- Spacebar: Increment count for Lycopodium.



*This free application has been developed by Thomas Akabane in Python using DeepSeek and ChatGPT*


Enjoy using the Pollen Grain Counter!


If you would like to report any problems concerning the application contact: thomask.akabane@gmail.com
"""

help_label = tk.Label(help_frame, text=help_text, font=("Arial", 10), anchor="w", justify="left")
help_label.pack(padx=10, pady=10)

###################################

root.mainloop()