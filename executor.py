import subprocess
import json

def run(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return out.decode()
    except subprocess.CalledProcessError as e:
        return f"ERROR:\n{e.output.decode()}"

def execute_task():

    with open("infrastructure/commands.json") as f:
        data = json.load(f)

    print(f"\n=== Running Task: {data['task']} ===\n")

    for step in data["steps"]:
        print(f"> {step}")
        print(run(step))

    print("\n=== VALIDATION ===\n")

    for check in data["validation"]:
        print(f"> {check}")
        print(run(check))

if __name__ == "__main__":
    execute_task()
