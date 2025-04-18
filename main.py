import random
import tkinter as tk
from tkinter import ttk
from numpy import percentile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Tuple


class DiceRolls:
    @staticmethod
    def roll_dice(num_dice: int) -> List[int]:
        return [random.randint(1, 6) for _ in range(num_dice)]

    @staticmethod
    def reroll_dice(rolls: List[int], reroll_option: str, threshold: int) -> List[int]:
        if reroll_option == "1":
            return [random.randint(1, 6) if r == 1 else r for r in rolls]
        elif reroll_option == "6":
            return [random.randint(1, 6) if r == 6 else r for r in rolls]
        elif reroll_option == "positive":
            return [random.randint(1, 6) if r >= threshold else r for r in rolls]
        elif reroll_option == "negative":
            return [random.randint(1, 6) if r < threshold else r for r in rolls]
        return rolls

    @staticmethod
    def check_criteria(rolls: List[int], threshold: int, saver_roll:bool) -> int:
        if saver_roll:
            return sum(1 for r in rolls if r<threshold)
        else:
            return sum(1 for r in rolls if r >= threshold)

    @staticmethod
    def run_experiment(num_dice: int, reroll_option: str, threshold: int, save_roll: bool) -> Tuple[int, int]:


        rolls = DiceRolls.roll_dice(num_dice)
        rolls = DiceRolls.reroll_dice(rolls, reroll_option, threshold)
        return DiceRolls.check_criteria(rolls, threshold, save_roll), rolls.count(6)


class DiceSimulatorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dice roll simulator")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.RIGHT, padx=10)

        self.setup_controls()

    def setup_controls(self):
        self.dice_entry = tk.Entry(self.left_frame)
        tk.Label(self.left_frame, text="Dice amount:").pack()
        self.dice_entry.pack()
        self.dice_entry.insert(0, "5")

        self.threshold_entries = []
        self.reroll_vars = []

        self.poison_var = tk.BooleanVar()
        self.fury_var = tk.BooleanVar()
        self.lethal_var = tk.BooleanVar()
        self.reg_var = tk.BooleanVar()

        labels = ["To Hit (1 = auto hit)", "To Wound (1 = auto wound)", "Armor Save (7 = no save)", "Special Save (7 = no save)"]

        for i, label in enumerate(labels):
            frame = tk.Frame(self.left_frame, relief=tk.RIDGE, borderwidth=2)
            frame.pack(pady=5, padx=10, fill=tk.X)
            tk.Label(frame, text=label).pack()

            entry = tk.Entry(frame)
            entry.insert(0, "4")
            entry.pack()
            self.threshold_entries.append(entry)

            reroll_var = tk.StringVar(value="none")
            self.reroll_vars.append(reroll_var)

            tk.Label(frame, text="Reroll:").pack()
            for text, value in [("1", "1"), ("6", "6"), ("Reroll positive", "positive"), ("Reroll negative", "negative"), ("No rerolls", "none")]:
                ttk.Radiobutton(frame, text=text, variable=reroll_var, value=value).pack(anchor=tk.W)

            if i == 0:
                tk.Checkbutton(frame, text="Poison", variable=self.poison_var).pack()
                tk.Checkbutton(frame, text="Fury", variable=self.fury_var).pack()
            elif i == 1:
                tk.Checkbutton(frame, text="Lethal", variable=self.lethal_var).pack()
            elif i == 3:
                tk.Checkbutton(frame, text="Regeneration", variable=self.reg_var).pack()

        tk.Button(self.root, text="Run simulation", command=self.run_simulation).pack()

    def run_simulation(self):
        num_experiments = 1000
        plot_data = []

        for _ in range(num_experiments):
            results = [0, 0, 0, 0]
            num_dice = int(self.dice_entry.get())

            for i in range(4):
                save_roll = i > 1
                threshold = int(self.threshold_entries[i].get())
                reroll = self.reroll_vars[i].get()

                successes, sixes = DiceRolls.run_experiment(num_dice, reroll, threshold, save_roll)
                results[i] += successes

                if i == 0:
                    if self.poison_var.get():
                        results[0] -= sixes
                        results[2] += sixes
                    if self.fury_var.get():
                        results[0] += sixes
                if i == 1 and self.lethal_var.get():
                    results[1] -= sixes
                    if self.reg_var.get():
                        results[3] += sixes
                    else:
                        results[2] += sixes

                num_dice = results[i]

            plot_data.append(results[3])

        self.plot_results(plot_data, num_experiments)

    def plot_results(self, data: List[int], total: int):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        counts = {i: data.count(i) for i in range(min(data), max(data) + 1)}
        percentages = [c / total * 100 for c in counts.values()]

        fig, ax = plt.subplots()
        ax.bar(counts.keys(), percentages, edgecolor='black')
        ax.set_title("Probability of roll")
        ax.set_xlabel("Success number")
        ax.set_ylabel("Percent (%)")

        percentile_text = "\n".join([
            f"99%: {percentile(data, 1):.2f}\n"
            f"90%: {percentile(data, 10):.2f}\n"
            f"75%: {percentile(data, 25):.2f}\n"
            f"50%: {percentile(data, 50):.2f}\n"
            f"25%: {percentile(data, 75):.2f}\n"
            f"10%: {percentile(data, 90):.2f}\n"
            f"1%: {percentile(data, 99):.2f}"
        ])

        plt.figtext(0.75, 0.60, percentile_text, bbox={"facecolor": "orange", "alpha": 0.5}, fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


if __name__ == "__main__":
    app = DiceSimulatorUI()
    app.root.mainloop()
