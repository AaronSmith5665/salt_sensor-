from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    'packages': ['flask', 'os', 'datetime', 'time'],  # Add any additional packages used
    'excludes': ['tkinter'],  # Exclude any modules not needed
}

setup(
    name="Water Tank Salt Sensor Monitor",
    version="0.1",
    description="The Water Tank Salt Sensor Monitor is a smart, web-based application",
    options={"build_exe": build_exe_options},
    executables=[Executable("sensordesktop.py", base="Win32GUI")]
)
