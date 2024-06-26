# Import modules
import os
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from pathlib import Path
import re
import PyPDF2

# Function to open a PDF file  
def open_pdf(pdf_path: Path):
    # Get the path to the file as a string
    pdf_path_string = pdf_path.as_posix()

    # Get the extension of the file
    ext = pdf_path.suffix

    # Check if the file is a PDF
    if ext != '.pdf':
        messagebox.showwarning("Warning", "File must be a PDF!")
        return
    
    # Open the PDF file
    try:
        pdf_file = open(pdf_path_string, 'rb')
    except FileNotFoundError:
        messagebox.showwarning("Warning", "File not found!")
        return
    except PermissionError:
        messagebox.showwarning("Warning", "Permission denied!")
        return
    else:
        print('PDF file opened')

    return pdf_file

# Function for delete pages dialouge
def delete_pages(pdf_in: PyPDF2.PdfFileReader, new_file_path: str):

    pdf_in_list = pdf_in.pages

    # Create a PdfFileWriter object to write pages to a new PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Open Options Dialouge
    pages_to_delete_str = simpledialog.askstring("Delete Pages", "Enter the pages or page range to delete separated by commas, no spaces.")

    # If nothing is entered, do not continue
    if pages_to_delete_str is None or pages_to_delete_str == "":
        return

    # If there is input, process into a list of strings
    pages_to_delete_str_list = delete_input_to_str_list(pages_to_delete_str)

    # Turn list of strings into a usable, sorted list of integers 
    pages_to_delete_int_list = strlist_to_intlist(pages_to_delete_str_list, len(pdf_in_list))

    if pages_to_delete_int_list == None:
        return
    

    print("Deleting Pages")

    page_num = 1
    
    for page in pdf_in_list:

        # If pages_to_delete_int_list is empty, go ahead and add page
        if pages_to_delete_int_list == []:
            print("Adding page " + str(page_num))
            pdf_writer.add_page(page)


        # If pages_to_delete_int is not empty, check the head to see if page should be added
        else:
            # Do not add page if it is in pages_to_delete_int
            if page_num != pages_to_delete_int_list[0]:
                print("Adding page " + str(page_num))
                pdf_writer.add_page(page)
            # Remove first element in list
            else:
                pages_to_delete_int_list.pop(0)
        
        # Increment page number
        page_num += 1
                
    # save the new pdf file
    with open(new_file_path, 'wb') as f:
        pdf_writer.write(f)

# Function for turning delete input into a list of strings
def delete_input_to_str_list(pages_to_delete_str: str) -> list:
    pages_to_delete_list = pages_to_delete_str.split(",")

    result = []
    
    for x in pages_to_delete_list:
        result.append(x)

    return result

# Turn list of strings into a usable, sorted list of integers in ascending order
# Returns an null if any input is invalid
# Input is valid if:
# Input consits of a single integer ex: 1, 5, 99
# Input consits of a range in ascending order where the lower bound != the upper bound ex: 1-5, 7-8
# In any other senario, input is invalid and an empty list is returned
def strlist_to_intlist(pages_to_delete_str_list: str, totalPages: int) -> list:

    range_pattern = r'^\d+-\d+$'

    result = []

    # Check if the current input mathces the range format ex: 1-5
    for currInput in pages_to_delete_str_list:
        
        # If the input is in range format
        if re.match(range_pattern, currInput):
            print("Range Format")
            print("Lower: " + currInput[0])
            print("Upper: " + currInput[-1])

            # Cast the lower and upper bounds into ints
            lower_bound = int(currInput[0])
            upper_bound = int(currInput[-1])

            # lower_bound must be lower than upper bound
            if lower_bound >= upper_bound:
                messagebox.showwarning("Warning", "Invalid Input!")
                return None
            
            # Input range is valid, append each number in range to result list
            for i in range(lower_bound, upper_bound+1):
                
                # If there is a duplicate page number, throw error and return none
                if i in result:
                    messagebox.showwarning("Warning", "Invalid Input!")
                    return None
                
                # Input is valid, add to result
                result.append(i)
                print("Adding " + str(i))
           
        # If the input is in single page number format
        else:
            print("Single Page format")

            # Attempt to cast the string into an int
            try:
                page_number = int(currInput)
            # Invalid input if string is not convertable to int
            except ValueError:
                messagebox.showwarning("Warning", "Invalid Input!")
                return None
            else:
                # Invalid input if there is a duplicate number 
                if page_number in result:
                    messagebox.showwarning("Warning", "Invalid Input!")
                    return None
                # Valid input, add to result
                else:
                    result.append(page_number)
                    print("Adding " + str(page_number))
    
    # Sort list
    result.sort()

    # Check if each i is in a valid range valid [1,last_page_number]
    for i in result:
        if i <= 0:
            messagebox.showwarning("Warning", "Invalid Input!")
            return None
        elif i > totalPages:
            messagebox.showwarning("Warning", "Invalid Input!")
            return None
        
    # Debug
    print("Result")
    for x in result:
        print(x)

    return result

# Function to be called when the delete button is clicked
def del_on_button_click() -> None:
    print('Delete PDFs selected')
    # Show an "Open" dialog box and return the path to the selected file
    print('Asking for PDF file')
    pdf_path_string = askopenfilename()

    # Create a Path object from the string
    pdf_path = Path(pdf_path_string)

    # Open the PDF file with open_pdf function and create a reader object
    pdf_file = open_pdf(pdf_path)

    # If there is no file, return
    if pdf_file == None:
        return

    # Prompt the user for a save location and filename
    print('Asking for new location to save new file to')
    new_file_path = filedialog.asksaveasfilename(initialfile=".pdf", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

    # If user presses cancel, return
    if not new_file_path:
        return

    # Create a reader object from the file
    pdf_file_reader_in = PyPDF2.PdfReader(pdf_file)

    # Call Delete pages function
    delete_pages(pdf_file_reader_in, new_file_path)

    # Close the file
    pdf_file.close()

# Function for choosing and adding pdf to merge instance
def add_pdf_on_click(merger: PyPDF2.PdfMerger) -> None:
    
    # Let user choose pdf
    pdf_path_string = askopenfilename()

    # Turn path string into path object
    pdf_file_path = Path(pdf_path_string)

    # Attempt to open the file and store in PDF object
    pdf_file = open_pdf(pdf_file_path)

    # If open_pdf failed, do not continue
    if pdf_file == None:
        return

    # Add PDF to merger instance
    merger.append(PyPDF2.PdfReader(pdf_file))

    # Debug statement
    print('Adding PDF to merger instance')

    # Close PDF
    pdf_file.close()

# Function for choosing and adding pdf to merge instance
def save_as_pdf_on_click(merger: PyPDF2.PdfMerger) -> None:
    
    # Write the merged PDF to a new file
    output = open('merged.pdf', 'wb')
    merger.write(output)


# Function to be called when the merge button is clicked
def merge_on_button_click(root) -> None:
    print('Merge PDFs selected')

    print('Showing merge options')

    # Build merge PDFs dialouge
    dialog = tk.Toplevel(root)
    dialog.title("Merge PDFs")
    dialog.geometry("300x100")

    # Create Merger
    merger = PyPDF2.PdfMerger()

    # Add Pdf button
    add_pdf_button = tk.Button(dialog, text="Add PDF", command=lambda:add_pdf_on_click(merger))
    add_pdf_button.pack(pady=10)

    # Save as Pdf button
    save_as_PDF = tk.Button(dialog, text="Save as PDF", command=lambda:save_as_pdf_on_click(merger))
    save_as_PDF.pack(pady=10)

    dialog.grab_set()  # Make the dialog modal
    root.wait_window(dialog)  # Wait for the dialog to be closed


# Create the main window
root = tk.Tk()
# Set the title of the window
root.title("PDF Tools")

root.geometry("400x150")

# Create and add a delete PDF's button widget with specified text and command
delete_button = tk.Button(root, text="Delete Pages", command=del_on_button_click)

# Create and add a merge PDF's button widget with specified text and command
merge_button = tk.Button(root, text="Merge Pages", command=lambda:merge_on_button_click(root))

# Pack the button widgets to add it to the window and set padding
delete_button.pack(pady=10)

merge_button.pack(pady=10)

# Run the main loop to display the window and handle events
root.mainloop()
