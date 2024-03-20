# Import modules
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from pathlib import Path
import queue
import PyPDF2

# Function to be called when the button is clicked
def del_on_button_click() -> None:
    # Show an "Open" dialog box and return the path to the selected file
    pdf_path_string = askopenfilename()

    # Create a Path object from the string
    pdf_path = Path(pdf_path_string)

    # Open the PDF file with open_pdf function and create a reader object
    pdf_file = open_pdf(pdf_path)

    # If pdf file exists, continue
    if pdf_file != None:
        # Create a reader object from the file
        pdf_file_reader_in = PyPDF2.PdfReader(pdf_file)

        # Call Delete pages function
        delete_pages(pdf_file_reader_in)

        # Close the file
        pdf_file.close()
    
# Function to open a PDF file  
def open_pdf(pdf_path: Path):
    # Get the path to the file as a string
    pdf_path_string = pdf_path.as_posix()

    # Get the extension of the file
    ext = pdf_path.suffix

    # Check if the file is a PDF
    if ext != '.pdf':
        messagebox.showerror("Error", "File must be a PDF!")
        return
    
    # Open the PDF file
    try:
        pdf_file = open(pdf_path_string, 'rb')
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found")
        return
    except PermissionError:
        messagebox.showerror("Error", "Permission denied")
        return
    else:
        print('PDF file opened')

    return pdf_file

# Function for processing delete window input
def process_delete_input(pages_to_delete_str: str) -> list:
    pages_to_delete_list = pages_to_delete_str.split(",")

    result = queue.Queue()
    
    for x in pages_to_delete_list:
        result.put(int(x))

    return result

# Function for delete pages dialouge
def delete_pages(pdf_in: PyPDF2.PdfFileReader):

    pdf_in_list = pdf_in.pages

    # Create a PdfFileWriter object to write pages to a new PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Open Options Dialouge
    pages_to_delete_str = simpledialog.askstring("Delete Pages", "Enter the pages to delete separated by commas, no spaces")

    pages_to_delete_int = process_delete_input(pages_to_delete_str)

    page_num = 1
    
    for page in pdf_in_list:

        # If pages_to_delete_int is empty, go ahead and add page
        if pages_to_delete_int.empty():
            print("Adding page " + str(page_num))
            pdf_writer.add_page(page)


        # If pages_to_delete_int is not empty, check the head to see if page should be added
        else:
            # Do not add page if it is in pages_to_delete_int
            if page_num != pages_to_delete_int.queue[0]:
                print("Adding page " + str(page_num))
                pdf_writer.add_page(page)
            # dequeue
            else:
                pages_to_delete_int.get()
        
        # Increment page number
        page_num += 1
                
    # save the new pdf file
    with open('new_file.pdf', 'wb') as f:
        pdf_writer.write(f)

    

# Create the main window
root = tk.Tk()
# Set the title of the window
root.title("PDF Tools")

root.geometry("500x500")

# Create and add a Merge PDF's button widget with specified text and command
button = tk.Button(root, text="Delete Pages", command=del_on_button_click)
# Pack the button widget to add it to the window and set padding
button.pack(pady=10)



# Run the main loop to display the window and handle events
root.mainloop()
