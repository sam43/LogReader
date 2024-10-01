import re
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, filedialog, messagebox

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")
        self.root.geometry("950x740")

        # Initialize filter options
        self.filter_options_rand = {
            'okhttp': 'green',
            'CrashlyticsHelper': 'red',
            'Stream': 'blue',
            'ViewModel': 'yellow',
            'Firebase': 'orange',
            'Network': 'gray',
            'Camera': 'cyan'
        }

        self.filter_options = OrderedDict(sorted(self.filter_options_rand.items()))
        self.log_entries = []

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Create frames for tabs
        self.all_tab = tk.Frame(self.notebook)
        self.preset_tab = tk.Frame(self.notebook)
        self.notebook.add(self.all_tab, text="All")
        self.notebook.add(self.preset_tab, text="Preset Filters")

        # Build the All tab interface
        self.build_all_tab()

        # Build the Preset Filters tab interface
        self.build_preset_tab()

        self.load_button = tk.Button(self.root, text="Browse Log File", command=self.browse_file)
        self.load_button.pack(pady=10)

    def build_all_tab(self):
        self.custom_filter_entry = tk.Entry(self.all_tab, width=20)
        self.custom_filter_entry.pack(pady=10)

        self.apply_custom_filter_button = tk.Button(self.all_tab, text="Apply Custom Filter", command=self.add_new_filter)
        self.apply_custom_filter_button.pack(pady=10)

        self.tree_all = self.create_treeview(self.all_tab)

    def build_preset_tab(self):
        self.filter_var = tk.StringVar()
        self.filter_var.set('Select Filter')

        self.filter_dropdown = tk.OptionMenu(self.preset_tab, self.filter_var, *self.filter_options.keys(), 'Select Filter')
        self.filter_dropdown.pack(pady=10)
        self.filter_var.trace_add('write', self.apply_filter)

        self.tree_preset = self.create_treeview(self.preset_tab)

    def create_treeview(self, parent):
        tree_frame = tk.Frame(parent)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=('Log',), show='tree', height=20)
        tree.heading('#0', text='Log Entries')
        tree.column('#0', width=1500, stretch=tk.YES)

        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)

        tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(expand=True, fill=tk.BOTH)

        return tree

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log")])
        if file_path:
            self.log_entries = self.load_log_file(file_path)
            self.display_log_all()
            self.display_log_preset()

    def load_log_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except Exception as e:
            return [f"Error loading file: {str(e)}"]

    def display_log_all(self):
        self.tree_all.delete(*self.tree_all.get_children())

        # Regular expression to capture date and time (assuming format 'YYYY-MM-DD HH:MM:SS')
        datetime_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'

        grouped_logs = {}

        for line in self.log_entries:
            # Extract the date-time prefix if available
            match = re.match(datetime_pattern, line)
            if match:
                date_time = match.group(0)
                # Initialize a new list for this date-time if not already present
                if date_time not in grouped_logs:
                    grouped_logs[date_time] = []
                # Add the log entry without the date-time prefix
                grouped_logs[date_time].append(line[len(date_time):].strip())
            else:
                # Handle logs without a date-time prefix
                if "Unknown Time" not in grouped_logs:
                    grouped_logs["Unknown Time"] = []
                grouped_logs["Unknown Time"].append(line.strip())

        # Insert the grouped logs into the TreeView
        for date_time, logs in grouped_logs.items():
            # Create a parent item for each date-time group
            group_id = self.tree_all.insert('', tk.END, text=date_time, tags=('group_header',), open=True)

            # Add each log entry under the corresponding group
            for log in logs:
                self.tree_all.insert(group_id, tk.END, text=log, tags=('normal_text',))

        # Configure styles
        self.tree_all.tag_configure('group_header', foreground='blue', font=('Helvetica', 13, 'bold'))
        self.tree_all.tag_configure('normal_text', foreground='white', font=('Helvetica', 13))

    def display_log_preset(self, filter_keyword=None):
        self.tree_preset.delete(*self.tree_preset.get_children())

        filter_logs = {}
        for line in self.log_entries:
            line_lower = line.lower()

            for keyword, color in self.filter_options.items():
                if keyword.lower() in line_lower and (
                        filter_keyword is None or keyword.lower() == filter_keyword.lower()):
                    if keyword not in filter_logs:
                        filter_logs[keyword] = []

                    filter_logs[keyword].append(line)
                    break

        for keyword, logs in filter_logs.items():
            section_id = self.tree_preset.insert('', 'end', text=keyword.title(), open=True)
            for log in logs:
                start_index = log.lower().find(keyword.lower())
                end_index = start_index + len(keyword)

                # Split the line into parts: before, match, and after
                before_match = log[:start_index]
                matched_text = log[start_index:end_index]
                after_match = log[end_index:]

                item_id = self.tree_preset.insert(section_id, tk.END, text=before_match, tags=('normal_text',))
                self.tree_preset.insert(item_id, tk.END, text=matched_text, tags=('highlight_text',))
                self.tree_preset.insert(item_id, tk.END, text=after_match, tags=('normal_text',))

        # Apply styles for the preset tab
        self.tree_preset.tag_configure('highlight_text', foreground='red', font=('Helvetica', 13, 'bold'))
        self.tree_preset.tag_configure('normal_text', foreground='white', font=('Helvetica', 13))

    def apply_filter(self, *args):
        selected_filter = self.filter_var.get()
        if selected_filter != 'Select Filter':
            self.display_log_preset(selected_filter)
        else:
            self.display_log_preset()

    def add_new_filter(self):
        new_filter = self.custom_filter_entry.get().strip()
        if new_filter:
            # Check if the filter is already in the preset filters
            if new_filter not in self.filter_options:
                confirmation = messagebox.askquestion("Add Filter", f"Do you want to add '{new_filter}' as a filter?")
                if confirmation == 'yes':
                    # Add to preset filters with an unused color
                    txt_color = self.get_unused_color()
                    self.filter_options[new_filter] = txt_color
                    self.filter_dropdown['menu'].add_command(label=new_filter,
                                                             command=tk._setit(self.filter_var, new_filter))
                    self.filter_var.set(new_filter)
                    self.display_custom_filtered_log(new_filter)
                else:
                    # Display logs matching the custom filter without adding to presets
                    self.display_custom_filtered_log(new_filter)
            else:
                # If the filter already exists, show logs that match this filter
                self.display_custom_filtered_log(new_filter)

    def display_custom_filtered_log(self, custom_filter):
        self.tree_all.delete(*self.tree_all.get_children())
        highlight_color = 'red'  # Text color for the highlighted keyword

        # Regular expression to capture date and time (assuming format 'YYYY-MM-DD HH:MM:SS')
        datetime_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        grouped_logs = {}

        for line in self.log_entries:
            if custom_filter.lower() in line.lower():
                # Extract the date-time prefix if available
                match = re.match(datetime_pattern, line)
                date_time = match.group(0) if match else "Unknown Time"

                if date_time not in grouped_logs:
                    grouped_logs[date_time] = []

                # Remove date-time from line for display
                log_content = line[len(date_time):].strip() if match else line.strip()

                # Highlighting: Ensure the entire line is kept intact
                start_index = log_content.lower().find(custom_filter.lower())
                if start_index != -1:
                    end_index = start_index + len(custom_filter)

                    # Split the log content into before, match, and after segments
                    before_match = log_content[:start_index]
                    matched_text = log_content[start_index:end_index]
                    after_match = log_content[end_index:]

                    grouped_logs[date_time].append((before_match, matched_text, after_match))

        # Insert the grouped logs into the TreeView
        for date_time, logs in grouped_logs.items():
            # Create a parent item for each date-time group
            group_id = self.tree_all.insert('', tk.END, text=date_time, tags=('group_header',), open=True)

            # Add each log entry as a single item with the highlighted text within
            for before_match, matched_text, after_match in logs:
                combined_text = before_match + matched_text + after_match

                # Insert the complete line under the group
                item_id = self.tree_all.insert(group_id, tk.END, text=combined_text, tags=('normal_text',))

                # Apply the tag for the matching part
                self.tree_all.tag_configure('highlight_text', foreground=highlight_color,
                                            font=('Helvetica', 16, 'bold'))

                # Display the log entry with highlighting only the matched keyword
                self.tree_all.item(item_id, tags=('highlight_text',))

        # Configure styles
        self.tree_all.tag_configure('group_header', foreground='blue', font=('Helvetica', 16, 'bold'))
        self.tree_all.tag_configure('normal_text', foreground='black', font=('Helvetica', 16))

    def get_unused_color(self):
        used_colors = set(self.filter_options.values())
        available_colors = ['green', 'red', 'blue', 'gray', 'yellow', 'cyan', 'orange']
        for color in available_colors:
            if color not in used_colors:
                return color
        return 'white'

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()