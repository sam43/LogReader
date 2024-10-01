import tkinter as tk


def create_text_view(root):
    text_view = tk.Text(root, wrap=tk.WORD)
    text_view.pack(fill=tk.BOTH, expand=True)

    # Insert some sample text
    sample_text = (
        "This is a sample text that demonstrates text wrapping in a Tkinter Text widget. "
        "The wrap=tk.WORD option allows the text to wrap at word boundaries."
    )
    text_view.insert(tk.END, sample_text)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Text View with Text Wrapping")

    create_text_view(root)

    root.mainloop()
