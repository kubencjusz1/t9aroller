import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from numpy import percentile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def roll_dice(num_dice):
    return [random.randint(1, 6) for _ in range(num_dice)]


def reroll_dice(rolls, reroll_option, threshold):
    if reroll_option == "1":
        return [random.randint(1, 6) if roll == 1 else roll for roll in rolls]
    elif reroll_option == "6":
        return [random.randint(1, 6) if roll == 6 else roll for roll in rolls]
    elif reroll_option == "positive":
        return [random.randint(1, 6) if roll >= threshold else roll for roll in rolls]
    elif reroll_option == "negative":
        return [random.randint(1, 6) if roll < threshold else roll for roll in rolls]
    return rolls


def check_criteria(rolls, threshold):
    return sum(1 for roll in rolls if roll >= threshold)


def run_experiment(num_dice, reroll_option, threshold, j):
    if j < 2:
        rolls = roll_dice(num_dice)
        rolls = reroll_dice(rolls, reroll_option, threshold)
        success_count = check_criteria(rolls, threshold)
        number_of_6 = rolls.count(6)
        return success_count, number_of_6

    elif j > 1:
        if reroll_option == "1":
            reroll_option = "6"
        elif reroll_option == "6":
            reroll_option = "1"
        elif reroll_option == "positive":
            reroll_option = "negative"
        elif reroll_option == "negative":
            reroll_option = "positive"
        threshold = 8 - threshold
        rolls = roll_dice(num_dice)
        rolls = reroll_dice(rolls, reroll_option, threshold)
        success_count = check_criteria(rolls, threshold)
        number_of_6 = rolls.count(6)
        return success_count, number_of_6


def plot_histogram(results, num_experiments, canvas_frame):
    counts = {i: results.count(i) for i in range(min(results), max(results) + 1)}
    percentages = [count / num_experiments * 100 for count in counts.values()]

    fig, ax = plt.subplots()
    percentile_info = (
        f"99%: {percentile(results, 1):.2f}\n"
        f"90%: {percentile(results, 10):.2f}\n"
        f"75%: {percentile(results, 25):.2f}\n"
        f"50%: {percentile(results, 50):.2f}\n"
        f"25%: {percentile(results, 75):.2f}\n"
        f"10%: {percentile(results, 90):.2f}\n"
        f"1%: {percentile(results, 99):.2f}"
    )
    plt.figtext(0.75, 0.60, percentile_info, bbox={"facecolor": "orange", "alpha": 0.5, "pad": 5}, fontsize=10)
    ax.bar(counts.keys(), percentages, edgecolor='black', alpha=0.75)
    ax.set_xlabel("Liczba kości spełniających warunek")
    ax.set_ylabel("Procent wystąpień")
    ax.set_title("Prawdopodobieństwo danego rezultatu")

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def run_simulation():
    num_experiments = 1000
    plot_data = []
    for j in range(num_experiments):
        results = [0, 0, 0, 0]
        num_dice = int(dice_entry.get())
        for i in range(4):
            threshold = int(threshold_entries[i].get())
            reroll_option = reroll_vars[i].get()
            tmp, number_of_6 = run_experiment(num_dice, reroll_option, threshold, i)
            results[i] = results[i] + tmp
            if poison_var.get() and i == 0:
                print("P", results, number_of_6)
                results[0] = results[0] - number_of_6
                results[2] = results[2] + number_of_6
                print("P", results, number_of_6, "\n")
            if fury_var.get() and i == 0:
                print("F", results, number_of_6)
                results[0] = results[0] + number_of_6
                print("F", results, number_of_6, "\n")
            if lethal_var.get() and i == 1:
                print("L", results, number_of_6)
                results[1] = results[1] - number_of_6
                if reg_var.get():
                    results[3] = results[3] + number_of_6
                else:
                    results[2] = results[2] + number_of_6
                print("L", results, number_of_6, "\n")
            num_dice = results[i]
        plot_data.append(results[3])

    plot_histogram(plot_data, num_experiments, canvas_frame)


root = tk.Tk()
root.title("Symulacja Rzutu Kośćmi")

main_frame = tk.Frame(root)
main_frame.pack()

left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, padx=10)

dice_frame = tk.Frame(left_frame)
dice_frame.pack()
tk.Label(dice_frame, text="Liczba kości:").pack()
dice_entry = tk.Entry(dice_frame)
dice_entry.pack()
dice_entry.insert(0, "5")

threshold_entries = []
reroll_vars = []
labels = ["Trafienie(1-autohit)", "Zranienie(1-autowound)", "Armor Savy(7-brak save)", "Special Savy(7-brak save)"]

for i in range(4):
    frame = tk.Frame(left_frame, relief=tk.RIDGE, borderwidth=2)
    frame.pack(pady=5, padx=10, fill=tk.X)

    tk.Label(frame, text=labels[i]).pack()
    if i == 0:
        poison_var = tk.BooleanVar()
        poison_checkbox = tk.Checkbutton(frame, text="Poison", variable=poison_var)
        poison_checkbox.pack()
        fury_var = tk.BooleanVar()
        fury_checkbox = tk.Checkbutton(frame, text="Fury", variable=fury_var)
        fury_checkbox.pack()

    elif i == 1:
        lethal_var = tk.BooleanVar()
        lethal_checkbox = tk.Checkbutton(frame, text="Lethal", variable=lethal_var)
        lethal_checkbox.pack()
    elif i == 3:
        reg_var = tk.BooleanVar()
        reg_checkbox = tk.Checkbutton(frame, text="Regenka", variable=reg_var)
        reg_checkbox.pack()

    tk.Label(frame).pack()
    threshold_entry = tk.Entry(frame)
    threshold_entry.pack()
    threshold_entry.insert(0, "4")
    threshold_entries.append(threshold_entry)

    reroll_var = tk.StringVar(value="none")
    tk.Label(frame, text="Opcja przerzutu:").pack()
    reroll_frame = tk.Frame(frame)
    reroll_frame.pack()

    ttk.Radiobutton(reroll_frame, text="Przerzut 1", variable=reroll_var, value="1").pack(side=tk.LEFT)
    ttk.Radiobutton(reroll_frame, text="Przerzut 6", variable=reroll_var, value="6").pack(side=tk.LEFT)
    ttk.Radiobutton(reroll_frame, text="Przerzut pozytywnych", variable=reroll_var, value="positive").pack(side=tk.LEFT)
    ttk.Radiobutton(reroll_frame, text="Przerzut negatywnych", variable=reroll_var, value="negative").pack(side=tk.LEFT)
    ttk.Radiobutton(reroll_frame, text="Brak przerzutu", variable=reroll_var, value="none").pack(side=tk.LEFT)
    reroll_vars.append(reroll_var)

canvas_frame = tk.Frame(main_frame)
canvas_frame.pack(side=tk.RIGHT, padx=10)

tk.Button(root, text="Uruchom symulację", command=run_simulation).pack()

root.mainloop()
