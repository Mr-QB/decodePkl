import flet
import pandas as pd
from flet import AppBar, ElevatedButton, Page, Text, View, colors, Container
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Text,
    icons,
)
import os
import cv2
import numpy as np
import pickle
import shutil


def loadPkl(file_path):
    with open(file_path, "rb") as f:  # Use file path directly, no need for .value
        dataframe = pickle.load(f)
    return dataframe


def saveImage(dataframe, output_folder):
    output_folder += "/user_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # If it exists, remove all files in the folder
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            # Remove file or folder
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directory

    for index, row in dataframe.iterrows():
        for i, image in enumerate(row["images"]):
            if isinstance(image, np.ndarray):
                image_name = f"image_{row['userId']}_{i}.jpg"
                output_path = os.path.join(output_folder, image_name)

                cv2.imwrite(output_path, image)

            else:
                print(f"Image at index {i} is not a valid numpy array.")


def main(page: Page):
    page.title = "Routes Example"

    # Declare dataframe_table as global so it can be modified in the event handler
    dataframe_table = None
    dataframe = None

    def pick_files_result(e: FilePickerResultEvent):
        if e.files:  # Check if files are selected
            selected_files.value = ", ".join(map(lambda f: f.path, e.files))
            # selected_files.update()

            nonlocal dataframe_table  # Access the outer dataframe_table variable
            nonlocal dataframe  # Access the outer dataframe variable

            # Load the first file (assuming only one file is selected)
            dataframe = loadPkl(e.files[0].path)
            saveImage(dataframe, os.path.dirname(e.files[0].path))

        else:
            selected_files.value = "Cancelled!"
            selected_files.update()

    pick_files_dialog = FilePicker(on_result=pick_files_result)
    selected_files = Text()

    page.overlay.extend(
        [
            pick_files_dialog,
        ]
    )

    def route_change(e):
        page.views.clear()

        page.views.append(
            View(
                "/",
                [
                    Row(
                        [
                            ElevatedButton(
                                "Pick files",
                                icon=icons.UPLOAD_FILE,
                                on_click=lambda _: pick_files_dialog.pick_files(
                                    allow_multiple=True
                                ),
                            ),
                            # selected_files,
                        ],
                        expand=True,
                        alignment=flet.MainAxisAlignment.CENTER,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    ),
                ],
            )
        )

        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)


flet.app(main)
