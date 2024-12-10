import fitz  # PyMuPDF
import re
import csv
import ast
import os
import pickle
import shutil
# import logging

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)



# ETL - Extract Phase
def pdf_to_latex(pdf_path, start_page, end_page,tex_output_path):
    """
    Converts a range of pages from a PDF to LaTeX format.
    """
    doc = fitz.open(pdf_path)
    latex_content = []

    for page_num in range(start_page - 1, end_page):  # Adjusting for 0-based index
        page = doc[page_num]
        text = page.get_text("text")

        # Add LaTeX document structure for the first page
        if page_num == start_page - 1:
            latex_content.append(r"\documentclass{article}")
            latex_content.append(r"\usepackage[utf8]{inputenc}")
            latex_content.append(r"\begin{document}")

        # Add content of the page
        latex_content.append(f"\n% Page {page_num + 1}\n")
        latex_content.append(r"\begin{verbatim}")
        latex_content.append(text)
        latex_content.append(r"\end{verbatim}")

    # Add end of document
    latex_content.append(r"\end{document}")

    latex = "\n".join(latex_content)
    with open(tex_output_path, 'w', encoding='utf-8') as tex_file:
        tex_file.write(latex)
    return tex_output_path

# Transform Phase
def remove_specific_lines(file_path, output_path):
    """
    Removes specific LaTeX commands from a .tex file.
    """
    patterns_to_remove = [
        r'^\s*\\documentclass\b',
        r'^\s*\\usepackage\b',
        r'^\s*\\begin\{document\}',
        r'^\s*\\begin\{verbatim\}',
        r'^\s*\\end\{verbatim\}',
        r'^\s*\\end{document\}',
    ]
    compiled_patterns = [re.compile(pattern) for pattern in patterns_to_remove]

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Filter out lines matching the patterns
    filtered_lines = [line for line in lines if not any(pattern.match(line) for pattern in compiled_patterns)]

    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

    print("Specific LaTeX commands removed and cleaned content saved. in " ,output_path)


# 3 remove page number and lines
# def remove_page_number_lines(input_file, output_file):
    # with open(input_file, 'r', encoding='utf-8') as file:
    #     lines = file.readlines()

    # cleaned_lines = []
    # page_number = None

    # for line in lines:
    #     # Remove repetitive dots from the line
    #     # line = remove_repeated_dots(line)

    #     page_match = re.match(r'% Page (\d+)', line)
    #     if page_match:
    #         page_number = page_match.group(1)
    #         cleaned_lines.append(line)
    #         continue

    #     if page_number is not None and re.match(rf'^{page_number}$', line.strip()):
    #         continue

    #     cleaned_lines.append(line)

    # with open(output_file, 'w', encoding='utf-8') as file:
    #     file.writelines(cleaned_lines)

def remove_page_number_lines(input_file, output_file):
    import re  # Ensure the `re` module is imported if not already
    def remove_repeated_dots(line):
        # Assuming this function is defined elsewhere to remove repeated dots
        return re.sub(r'\.{2,}', '.', line)  # Example implementation
    
    def remove_links(line):
        # Remove URLs starting with http, https, or www
        return re.sub(r'https?://\S+|www\.\S+', '', line)
    
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cleaned_lines = []
    page_number = None

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Remove repetitive dots from the line
        line = remove_repeated_dots(line)
        # Remove links from the line
        line = remove_links(line)


        page_match = re.match(r'% Page (\d+)', line)
        if page_match:
            page_number = page_match.group(1)
            cleaned_lines.append(line)
            continue

        if page_number is not None and re.match(rf'^{page_number}$', line.strip()):
            continue

        cleaned_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)


def process_tex_file(file_path, headings, output_path):
    def is_number_line(line):
        """ Check if a line consists only of integers, decimals, or both, including multiple decimal points """
        return re.fullmatch(r'[\d.]+', line.strip()) is not None

    def remove_numbers(line):
        """ Remove all integers and decimals from a line """
        return re.sub(r'[\d.]+', '', line).strip()

    def match_heading(line, headings):
        """ Check if a line matches any of the given headings after removing numbers """
        stripped_line = remove_numbers(line)
        return any(stripped_line == heading.strip() for heading in headings)
    

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    lines_to_remove = []

    for i in range(len(lines)):
        current_line = lines[i].strip()


        if current_line.endswith('.'):
            continue

        if match_heading(current_line, headings):
            lines_to_remove.append(i)
            # print(f"Removing line {i}: {lines[i].strip()}")


            if i > 0 and is_number_line(lines[i - 1]) and not lines[i - 1].strip().endswith('.'):
                lines_to_remove.append(i - 1)
                # print(f"Removing adjacent number line {i-1}: {lines[i - 1].strip()}")

            if i < len(lines) - 1 and is_number_line(lines[i + 1]) and not lines[i + 1].strip().endswith('.'):
                lines_to_remove.append(i + 1)
                # print(f"Removing adjacent number line {i+1}: {lines[i + 1].strip()}")


    with open(output_path, 'w', encoding='utf-8') as file:
        for i, line in enumerate(lines):
            if i not in lines_to_remove:
                file.write(line)

def read_tex_file(file_path):
    paragraphs = []
    current_paragraph = []
    minimum_words = 5
    paragraph_started = False
    unused_lines = []
    page_number = None
    paragraph_number = 1
    paragraph_info = {}

    page_pattern = re.compile(r'% Page (\d+)')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            page_match = page_pattern.match(line)
            if page_match:
                page_number = page_match.group(1)
                continue

            if line:

                if not paragraph_started and len(line.split()) >= minimum_words:
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        paragraphs.append(paragraph_text)
                        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}
                        paragraph_number += 1
                        current_paragraph = []
                    current_paragraph.append(line)
                    paragraph_started = True
                elif paragraph_started:
                    current_paragraph.append(line)

                    if line.endswith('.'):

                        if len(current_paragraph) == 2:
                            continue

                        paragraph_text = ' '.join(current_paragraph)
                        paragraphs.append(paragraph_text)
                        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}
                        current_paragraph = []  
                        paragraph_number += 1  
                        paragraph_started = False  
                else:

                    unused_lines.append(line)


    if current_paragraph and current_paragraph[-1].endswith('.') and len(current_paragraph) > 1:
        paragraph_text = ' '.join(current_paragraph)
        paragraphs.append(paragraph_text)
        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}


    output_file_path = 'paragraphs_info.txt'
    with open(output_file_path, 'a', encoding='utf-8') as file:
        for num, info in paragraph_info.items():
            file.write(f"{{'Paragraph': {num}, 'Page': {info['Page']}, 'Text': '{info['Text']}'}}\n\n")

    print(f"Paragraph information has been appended to {output_file_path}")

def get_chapter_info(page_number,chapters):

    for start, end,name, number in chapters:
        if start <= page_number <= end:
            return number, name
    return 'Null', 'Null'

def get_topic_info(page_number,topics):
    for start, end, topic in topics:
        if start <= page_number <= end:
            return topic
    return 'Null'

def add_additional_info(input_file_path, output_file_path, headings, topics, book_name,book_auther):
    paragraphs = []
    
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                try:
                    paragraph = ast.literal_eval(line)
                    if isinstance(paragraph, dict):
                        if len(paragraph.keys())>0:
                            paragraphs.append(paragraph)
                except (ValueError, SyntaxError):
                    continue
    
    for i in range(len(headings)):
        headings[i] = (headings[i][0],headings[i][1],headings[i][2],i+1)
    # print("paragraphs ",paragraphs[0],"\n")
    print("headings " ,headings,"\n")
    for i, paragraph in enumerate(paragraphs, start=1):
        # print("paragraph ",paragraph) 
        page_number = (paragraph['Page'])

        chapter_number, chapter_name = get_chapter_info(page_number,headings)
        topic = get_topic_info(page_number,topics)
        # print(topic)
        
        paragraph['Paragraph'] = i
        paragraph['Chapter Number'] = chapter_number
        paragraph['Chapter Name'] = chapter_name
        paragraph['Topic'] = topic
        # change and make it variables
        paragraph['Book Name'] = book_name
        paragraph['Book Author'] = book_auther
        # paragraph['Book URL'] = book_url
    
    # print("finaly peragraph start from ",paragraphs[0],"\n")
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for paragraph in paragraphs:
            file.write(f"{paragraph}\n\n")
    
    print(f"Paragraphs have been updated and saved to {output_file_path}")

def read_tex_file(file_path,output_file_path):
    paragraphs = []
    current_paragraph = []
    minimum_words = 5
    paragraph_started = False
    unused_lines = []
    page_number = None
    paragraph_number = 1
    paragraph_info = {}

    page_pattern = re.compile(r'% Page (\d+)')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            page_match = page_pattern.match(line)
            if page_match:
                page_number = page_match.group(1)
                continue

            if line:

                if not paragraph_started and len(line.split()) >= minimum_words:
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        paragraphs.append(paragraph_text)
                        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}
                        paragraph_number += 1
                        current_paragraph = []
                    current_paragraph.append(line)
                    paragraph_started = True
                elif paragraph_started:
                    current_paragraph.append(line)

                    if line.endswith('.'):

                        if len(current_paragraph) == 2:
                            continue
                        paragraph_text = ' '.join(current_paragraph)
                        paragraphs.append(paragraph_text)
                        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}
                        current_paragraph = []  
                        paragraph_number += 1  
                        paragraph_started = False  
                else:

                    unused_lines.append(line)


    if current_paragraph and current_paragraph[-1].endswith('.') and len(current_paragraph) > 1:
        paragraph_text = ' '.join(current_paragraph)
        paragraphs.append(paragraph_text)
        paragraph_info[paragraph_number] = {'Text': paragraph_text, 'Page': page_number}


    # output_file_path = 'paragraphs_info.txt'
    with open(output_file_path, 'a', encoding='utf-8') as file:
        for num, info in paragraph_info.items():
            file.write(f"{{'Paragraph': {num}, 'Page': {info['Page']}, 'Text': '{info['Text']}'}}\n\n")

    print(f"Paragraph information has been appended to {output_file_path}")

    # Print all unused lines
    # if unused_lines:
    #     print("Unused lines:")
    #     for line in unused_lines:
    #         print(line)



# -------------------------------------------------------------------------- TOPICS EXTRECTION ----------------------------------------------------------------------
def extract_combined_lines(tex_file):
    with open(tex_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    extracted_data = []

    for i in range(len(lines) - 1):  # Iterate through lines with lookahead for the next line
        current_line = lines[i].strip()
        next_line = lines[i + 1].strip()

        # Check for the pattern: a topic and number on the first line and a page number on the next
        if re.match(r'^\d+\s+[A-Za-z].*$', current_line) and re.match(r'^\d+$', next_line):
            # Extract topic and start/end page
            match = re.match(r'^(\d+)\s+([A-Za-z].*)$', current_line)
            if match:
                start_page = int(match.group(1))
                topic = match.group(2).strip()
                end_page = int(next_line)
                extracted_data.append((start_page, end_page, topic))
    print("extrection done outcomes are ",extracted_data)
    return extracted_data


def remove_dots_and_numbers_from_tex(tex_file, output_file):
    with open(tex_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cleaned_lines = [re.sub(r'\b\d+(\.\d+)+\b|\.{1,}', '', line) for line in lines]

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)

def process_tex_file_for_topics(tex_file, output_file):
    with open(tex_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    data = []
    topics = []
    current_topic = None
    start_page = None

    for i in range(len(lines)):
        line = lines[i].strip()
        
  
        page_number_match = re.match(r'^\d+$', line)
        if page_number_match:
            page_number = int(line)
            

            if current_topic is not None and start_page is not None:
                end_page = page_number
                topics.append((current_topic, start_page, end_page - 1))
            
            start_page = page_number
            current_topic = None
        else:
       
            topic_name_match = re.match(r'^[A-Za-z].*$', line)
            if topic_name_match:
                current_topic = line

    if current_topic is not None and start_page is not None:
        topics.append((current_topic, start_page, ''))

    with open(output_file, 'w', encoding='utf-8') as file:
        for topic, start_page, end_page in topics:
            if end_page == '':
                data.append((start_page,end_page,topic))
                # file.write(f"Topic Name: {topic}\nPage No. {start_page}\n\n")
                file.write(f"({start_page}, {end_page},{str(topic)})\n\n")
            else:
                data.append((start_page,end_page,topic))
                # file.write(f"Topic Name: {topic}\nPage No. {start_page} to {end_page}\n\n")
                file.write(f"({start_page}, {end_page},{str(topic)})\n\n")

    return data

def sorted_headings(data1,heading):
    length = len(data1)
    for i in range(1,length):
        if data1[i-1][0]>data1[i][0]:
            heading.append(data1[i])
    # heading.append(data1[0])
    return heading

def headings_indexing_match(chapters):
    for i in range(len(chapters)):
        chapters[i]  = list(chapters[i])

    for i in range(1,len(chapters)):
        priviousChapter = chapters[i-1]
        currentChapter  = chapters[i]

        priviousChapter[1] = currentChapter[1]
        if type(currentChapter[1])==int:
            currentChapter[0] = int(currentChapter[1])+1
        
    for i in range(len(chapters)):
        chapters[i]  = tuple(chapters[i])
    return chapters

def remove_repeated_dots(text):
    pattern = r"\.\s*\.\s*\.\s*\.{1,}"
    return re.sub(pattern, "", text).strip()

# Load Phase
def txt_to_csv(input_file, output_file):

    with open(input_file, 'r', encoding='utf-8') as f:
        data = [ast.literal_eval(line.strip()) for line in f if line.strip()]

    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    fieldnames = sorted(all_keys)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            writer.writerow(item)

    print(f"CSV file has been created: {output_file}")

def csv_to_pkl_and_use(csv_input_file, pkl_output_file):
    print("enter in pkl file")
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(pkl_output_file), exist_ok=True)

    # Read the input CSV file
    data = []
    with open(csv_input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    # Write data to .pkl file
    with open(pkl_output_file, 'wb') as f:
        pickle.dump(data, f)

    print(f"PKL file has been created: {pkl_output_file}")




def topics_extrection(pdf_path, output_tex, start_page, end_page,tex_file_path_for_heading):
    pdf_to_latex(pdf_path,start_page,end_page,tex_file_path_for_heading)
    remove_specific_lines(tex_file_path_for_heading,tex_file_path_for_heading)
    remove_page_number_lines(tex_file_path_for_heading,tex_file_path_for_heading)
    # extracted_lines = extract_combined_lines(tex_file_path)
    # # append headings tupels
    # for entry in extracted_lines:
    #     heading.append(entry)
    # print("headings are ", heading)

    # again topi extrection
    remove_dots_and_numbers_from_tex(tex_file_path_for_heading,tex_file_path_for_heading)
    heading = extract_combined_lines(tex_file_path_for_heading)
    print("extract_combined_lines",heading)

    topics_tuple = process_tex_file_for_topics(tex_file_path_for_heading,tex_file_path_for_heading)

    heading = sorted_headings(topics_tuple,heading)
    # print("sorted_headings",heading)
    # now time to classify headings and topics
    # heading_array  = sorted_headings(topics_tuple,heading)
    return  topics_tuple,heading

def sub_topics(output_tex,headings):
    with open(output_tex, 'r') as file:
        lines = file.readlines()

    # Parse tuples from the file
    file_tuples = []
    for line in lines:
        # Convert the line into a tuple (basic parsing for this example)
        try:
            file_tuples.append((line.strip()))  # Use eval for simplicity, ensure the file is safe!
            # print(file_tuples)
        except:
            pass  # Skip lines that are not tuples

    # Filter tuples that are not in the character array
    return [tup for tup in file_tuples if tup not in headings]



def headings_classification(tex_file_path_for_heading,topics_arr,heading):
    
    extracted_lines = extract_combined_lines(tex_file_path_for_heading)
    
    for entry in extracted_lines:
        heading.append(entry)

    # print("headings are ", heading)
    # print("topics are ",topics_arr)
    # Headings Array
    sorted_heading = sorted_headings(topics_arr,heading)
    
    # sorted_heading = headings_indexing_match(sorted_heading)
    print("sorted headings  ",sorted_heading)
    # Sub Topics array
    sub_topics_arr = sub_topics(tex_file_path_for_heading,sorted_heading)
    return sorted_heading,sub_topics_arr



# Main Pipeline Execution
def execute_pipeline(pdf_path, output_tex, start_page, end_page, csv_output_path, topics_start,topics_end,tex_file_path_for_heading, book_name, book_auther,pkl_path):
    # Step 1: Convert PDF to LaTeX
    pdf_to_latex(pdf_path,start_page,end_page,output_tex)

    remove_specific_lines(output_tex, output_tex)
    remove_page_number_lines(output_tex, output_tex)
    # remove_dots_and_numbers_from_tex(output_tex,output_tex)

    # topics extrection
    topics_arr, headings = topics_extrection(pdf_path, tex_file_path_for_heading, topics_start, topics_end, tex_file_path_for_heading)
    headings = sorted(headings)
    headings = headings_indexing_match(headings)
    # print("length of topics arr ",headings)
    
    process_tex_file(output_tex, [entry[2] for entry in topics_arr],output_tex)

    read_tex_file(output_tex, output_tex)
    add_additional_info(output_tex, output_tex, headings, topics_arr, book_name, book_auther)
    
    # Step 3: Save cleaned text to CSV
    txt_to_csv(output_tex, csv_output_path)
    csv_to_pkl_and_use(csv_output_path, pkl_path)

# def process_pdfs_in_folder(folder_path, tex_file_path_for_heading,form_data):
#     # Create an output folder for CSV files
#     csv_output_folder = os.path.join(folder_path, "csv_outputs")
#     os.makedirs(csv_output_folder, exist_ok=True)

#     # Create an output folder for .tex files
#     tex_output_folder = os.path.join(folder_path, "tex_files")
#     os.makedirs(tex_output_folder, exist_ok=True)

#     # Iterate through all PDF files in the folder
#     for file_name in os.listdir(folder_path):
#         if file_name.endswith(".pdf"):
#             pdf_path = os.path.join(folder_path, file_name)
#             base_name = os.path.splitext(file_name)[0]
#             csv_output_path = os.path.join(csv_output_folder, f"{base_name}.csv")
#             tex_output_path = os.path.join(tex_output_folder, f"{base_name}.tex")

#             # Check if the CSV already exists
#             if os.path.exists(csv_output_path):
#                 print(f"Skipping '{file_name}' as it has already been processed.")
#                 continue

#             print(f"\nProcessing new PDF: {file_name}")

#             # Prompt user for input parameters for each PDF
#             topics_start = int(input(f"Enter the topics start index for '{file_name}': "))
#             topics_end = int(input(f"Enter the topics end index for '{file_name}': "))
#             start_page = int(input(f"Enter the start page for '{file_name}': "))
#             end_page = int(input(f"Enter the end page for '{file_name}': "))+start_page
#             book_name = input("Enter the book name: ")
#             book_author = input("Enter the book author: ")
#             # book_url = input("Enter the book URL: ")

#             # Execute the ETL pipeline for the current PDF
#             execute_pipeline(
#                 pdf_path,
#                 tex_output_path,  # Store the .tex file in the dedicated folder
#                 start_page,
#                 end_page,
#                 csv_output_path,
#                 topics_start,
#                 topics_end,
#                 tex_file_path_for_heading,
#                 book_name,
#                 book_author,
#                 book_url
#             )

#     print(f"\nAll new PDFs processed. CSV files are saved in: {csv_output_folder}")
#     print(f".tex files are saved in: {tex_output_folder}")


# def process_pdfs_in_folder(folder_path, tex_file_path_for_heading, form_data):
#     # Create an output folder for CSV files
#     csv_output_folder = os.path.join(folder_path, "csv_outputs")
#     os.makedirs(csv_output_folder, exist_ok=True)

#     # Create an output folder for .tex files
#     tex_output_folder = os.path.join(folder_path, "tex_files")
#     os.makedirs(tex_output_folder, exist_ok=True)

#     # Iterate through all PDF files in the folder
#     for file_name in os.listdir(folder_path):
#         if file_name.endswith(".pdf"):
#             pdf_path = os.path.join(folder_path, file_name)
#             base_name = os.path.splitext(file_name)[0]
#             csv_output_path = os.path.join(csv_output_folder, f"{base_name}.csv")
#             tex_output_path = os.path.join(tex_output_folder, f"{base_name}.tex")

#             # Check if the CSV already exists
#             if os.path.exists(csv_output_path):
#                 print(f"Skipping '{file_name}' as it has already been processed.")
#                 continue

#             print(f"\nProcessing new PDF: {file_name}")

#             # Get parameters from form_data
#             topics_start = form_data["chapter_start_page"]
#             topics_end = form_data["chapter_end_page"]
#             start_page = form_data["content_start_page"]
#             end_page = form_data["content_end_page"]
#             book_name = form_data["book_name"]
#             book_author = form_data["author_name"]

#             # Execute the ETL pipeline for the current PDF
#             execute_pipeline(
#                 pdf_path,
#                 tex_output_path,
#                 start_page,
#                 end_page,
#                 csv_output_path,
#                 topics_start,
#                 topics_end,
#                 tex_file_path_for_heading,
#                 book_name,
#                 book_author,
#             )

#     print(f"\nAll new PDFs processed. CSV files are saved in: {csv_output_folder}")
#     print(f".tex files are saved in: {tex_output_folder}")

def cleanup_directory(directory_path):
    """
    Deletes all files in the specified directory.
    """
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def process_pdfs_in_folder(folder_path, tex_file_path_for_heading, form_data):
    # Create an output folder for CSV files
    csv_output_folder = os.path.join(folder_path, "csv_outputs")
    os.makedirs(csv_output_folder, exist_ok=True)

    # Create an output folder for .tex files
    tex_output_folder = os.path.join(folder_path, "tex_files")
    os.makedirs(tex_output_folder, exist_ok=True)

    # Create an output folder for pickle files
    pkl_output_folder = os.path.join(folder_path, "pkl_file")
    os.makedirs(pkl_output_folder, exist_ok=True)

    # Iterate through all PDF files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            base_name = os.path.splitext(file_name)[0]
            csv_output_path = os.path.join(csv_output_folder, f"{base_name}.csv")
            tex_output_path = os.path.join(tex_output_folder, f"{base_name}.tex")
            pkl_file_path = os.path.join(pkl_output_folder, f"{base_name}.pkl")

            # Check if the CSV already exists
            if os.path.exists(csv_output_path):
                print(f"Skipping '{file_name}' as it has already been processed.")
                continue

            print(f"\nProcessing new PDF: {file_name}")

            # Get parameters from form_data
            topics_start = form_data["chapter_start_page"]
            topics_end = form_data["chapter_end_page"]
            start_page = form_data["content_start_page"]
            end_page = form_data["content_end_page"]
            book_name = form_data["book_name"]
            book_author = form_data["author_name"]
            
            # Execute the ETL pipeline for the current PDF
            execute_pipeline(
                pdf_path,
                tex_output_path,
                start_page,
                end_page,
                csv_output_path,
                topics_start,
                topics_end,
                tex_file_path_for_heading,
                book_name,
                book_author,
                pkl_file_path
            )

    print(f"\nAll new PDFs processed. CSV files are saved in: {csv_output_folder}")
    print(f".tex files are saved in: {tex_output_folder}")

    # finally:
    #     # Cleanup all output directories after processing
    #     print("\nCleaning up output directories...")
    #     cleanup_directory(csv_output_folder)
    #     cleanup_directory(tex_output_folder)
    #     cleanup_directory(pkl_output_folder)
    #     print("All temporary files have been deleted.")

# # Run the pipeline
# if __name__ == '__main__':
#     folder_path = "./"
#     tex_file_path_for_heading = "./heading_elements.tex"

    # Process all new PDFs in the folder
    # process_pdfs_in_folder(folder_path, tex_file_path_for_heading)