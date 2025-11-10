from tkinter import messagebox, simpledialog
from utils.id_generator import generate_new_ids_for_csv
from utils.identifiers import display_identifier_pools


class IDController:
    def __init__(self, app):
        self.app = app

    def generate_ids(self):
        selected_csv = self.app.csv_choice.get()
        if not selected_csv:
            messagebox.showwarning("No CSV selected", "Please select a CSV from the dropdown.")
            return

        num_new = simpledialog.askinteger(
            "Number of new IDs",
            "How many new IDs would you like to generate?",
            minvalue=1,
            maxvalue=10000
        )
        if not num_new:
            return

        try:
            generate_new_ids_for_csv(selected_csv, num_new=num_new, test_mode=self.app.test_mode.get())
            messagebox.showinfo("Success", f"Generated {num_new} new IDs for '{selected_csv}.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate IDs: {e}")

    def view_pools(self):
        try:
            text = display_identifier_pools()
            messagebox.showinfo("Identifier Pools", text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display pools: {e}")
