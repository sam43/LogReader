import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, filedialog, messagebox

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")

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

        self.filter_var = tk.StringVar()
        self.filter_var.set('Select Filter')

        self.filter_dropdown = tk.OptionMenu(root, self.filter_var, *self.filter_options.keys(), 'Select Filter')
        self.filter_dropdown.pack(pady=10)
        self.filter_var.trace_add('write', self.apply_filter)

        self.new_filter_entry = ttk.Entry(root, width=20)
        self.new_filter_entry.pack(pady=10)

        self.apply_new_filter_button = tk.Button(root, text="Apply New Filter", command=self.add_new_filter)
        self.apply_new_filter_button.pack(pady=10)

        self.canvas = tk.Canvas(root, height=300, width=800)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        self.tree = ttk.Treeview(self.frame, columns=('Log',), show='tree', height=30)
        self.tree.heading('#0', text='Log Entries')
        self.tree.column('#0', width=1000, minwidth=500, stretch=tk.YES)

        self.x_scrollbar = tk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.x_scrollbar.pack(side='bottom', fill=tk.BOTH, expand=True)
        self.tree.configure(xscrollcommand=self.x_scrollbar.set)

        self.y_scrollbar = tk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.y_scrollbar.pack(side='right', fill=tk.BOTH, expand=True)
        self.tree.configure(yscrollcommand=self.y_scrollbar.set)

        self.tree.pack(expand=True, fill=tk.BOTH)

        self.load_button = tk.Button(root, text="Browse Log File", command=self.browse_file)
        self.load_button.pack(pady=10)

        # Configure row and column weights for responsiveness
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log")])
        if file_path:
            self.log_entries = self.load_log_file(file_path)
            self.display_log()

    def load_log_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except Exception as e:
            return [f"Error loading file: {str(e)}"]

    def apply_filter(self, *args):
        selected_filter = self.filter_var.get()
        if selected_filter != 'Select Filter':
            self.display_log(selected_filter)
        else:
            self.display_log()

    def add_new_filter(self):
        new_filter = self.new_filter_entry.get()
        if new_filter and new_filter not in self.filter_options:
            confirmation = messagebox.askquestion("Add Filter", f"Do you want to add '{new_filter}' as a filter?")
            if confirmation == 'yes':
                color = self.get_unused_color()
                self.filter_options[new_filter] = color
                self.filter_dropdown['menu'].add_command(label=new_filter, command=tk._setit(self.filter_var, new_filter))
                self.filter_var.set(new_filter)
            else:
                self.display_log(new_filter)

    def get_unused_color(self):
        used_colors = set(self.filter_options.values())
        available_colors = ['green', 'red', 'blue', 'gray', 'yellow', 'cyan', 'orange']
        for color in available_colors:
            if color not in used_colors:
                return color
        return 'white'

    def display_log(self, filter_keyword=None):
        self.tree.delete(*self.tree.get_children())

        filter_logs = {}

        for line in self.log_entries:
            line_lower = line.lower()

            for keyword, color in self.filter_options.items():
                if keyword.lower() in line_lower and (filter_keyword is None or keyword.lower() == filter_keyword.lower()):
                    if keyword not in filter_logs:
                        filter_logs[keyword] = []

                    filter_logs[keyword].append(line)
                    break

        for keyword, logs in filter_logs.items():
            section_id = self.tree.insert('', 'end', text=keyword.title(), open=True)
            for log in logs:
                if filter_keyword and keyword.lower() == filter_keyword.lower():
                    self.tree.insert(section_id, tk.END, text=tk.Text(log, wrap=tk.WORD), tags=('plain_text',))
                else:
                    self.tree.insert(section_id, tk.END, text=tk.Text(log, wrap=tk.WORD), tags=(f'{color}_title',))

        self.tree.tag_configure('green_title', foreground='green', font=('bold'))
        self.tree.tag_configure('red_title', foreground='red', font=('bold'))
        self.tree.tag_configure('blue_title', foreground='blue', font=('bold'))
        self.tree.tag_configure('gray_title', foreground='gray', font=('bold'))
        self.tree.tag_configure('plain_text', foreground='white', font=('bold'))

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()
