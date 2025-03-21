import pandas as pd

history = []

def undo_last_action(df):
    if history:
        return history.pop()
    else:
        console.print("[bold red]❌ No previous actions to undo![/bold red]")
        return df

def save_state(df):
    history.append(df.copy())
