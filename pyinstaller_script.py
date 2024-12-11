import os
import sys
import subprocess

def compile_with_pyinstaller(
    script_name,
    output_dir="dist",
    icon_path=None,
    one_file=True,
    console=True,
    additional_options=None,
):
    """
    Compiles a Python script into an executable using PyInstaller.

    Parameters:
        script_name (str): Name of the Python script to compile (e.g., 'app.py').
        output_dir (str): Directory to save the compiled executable. Default is 'dist'.
        icon_path (str): Path to the icon file (.ico) for the executable. Default is None.
        one_file (bool): Whether to create a single executable file. Default is True.
        console (bool): Whether to include the console window. Default is True.
        additional_options (list): List of additional PyInstaller options. Default is None.
    """
    if not os.path.isfile(script_name):
        print(f"Error: Script '{script_name}' not found.")
        sys.exit(1)

    # Base PyInstaller command
    command = ["pyinstaller", script_name]

    # Add output directory
    command.extend(["--distpath", output_dir])

    # Add one-file option
    if one_file:
        command.append("--onefile")

    # Add console/windowed option
    if not console:
        command.append("--noconsole")

    # Add icon if specified
    if icon_path:
        if not os.path.isfile(icon_path):
            print(f"Error: Icon file '{icon_path}' not found.")
            sys.exit(1)
        command.extend(["--icon", icon_path])

    # Add any additional options
    if additional_options:
        command.extend(additional_options)

    # Run the command
    print("Running PyInstaller with the following command:")
    print(" ".join(command))
    result = subprocess.run(command, text=True)

    if result.returncode == 0:
        print(f"\nCompilation successful! Executable saved in '{output_dir}'.")
    else:
        print(f"\nCompilation failed with exit code {result.returncode}.")

if __name__ == "__main__":

    # Compile server
    compile_with_pyinstaller(
        script_name="server.py",
        output_dir="dist_server",
        icon_path="tic-tac-toe.ico",
        one_file=True,
        console=True
    )

    # Compile client
    compile_with_pyinstaller(
        script_name="client.py",
        output_dir="dist_client",
        icon_path="tic-tac-toe.ico",
        one_file=True,
        console=False,
        additional_options=["--add-data", "config.json;."]
    )
