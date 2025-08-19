import pymupdf
import os
import sys
import re
import string
import json

CONFIG_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json");

def get_name(page):
    return page.get_textbox(pymupdf.Rect(1.0 * 72, 1.97 * 72, 4.0 * 72, 2.2 * 72)).strip()
def get_name1(page):
    return page.get_textbox(pymupdf.Rect(0.5 * 72, 5 * 72, 3.25 * 72, 5.14 * 72)).strip()
# Prompts user for selection from a list or to enter custom value
# options a list of selection candidates
# a string to display what kind of value the custom value is
# returns a string that was selected or custom inputted
def prompt_selection_or_custom(options, value_type):
    for i in range(len(options)):
        print(f"{i}: {options[i]}")
    while True:
        if len(options) == 0:
            print("No options available.")
            user_input = input(f"Enter custom {value_type}: ")
        else:
            user_input = input(f"Enter selection number or custom {value_type}: ")
        try:
            selection = int(user_input)
            if 0 <= selection < len(options):
                confirm = input(f"\"{options[selection]}\" selected. is this correct? [y/N]: ")
                if confirm.lower() == "y":
                    return options[selection]
            else:
                confirm = input(f"input: \"{user_input}\". is this correct? [y/N]: ")
                if (confirm.lower() == "y"):
                    return user_input
        except ValueError:
            confirm = input(f"input: \"{user_input}\". is this correct? [y/N]: ")
            if (confirm.lower() == "y"):
                return user_input
def prompt_selection_or_custom_dept(pdf_name, matches, name_to_dept):
    option_to_dept = {}
    print(f"Are any of these {pdf_name}?:")
    for i in range(len(matches)):
        if i <= 25:
            print(f"{string.ascii_lowercase[i]}: {matches[i]}:\t{name_to_dept[matches[i]]}")
            option_to_dept[string.ascii_lowercase[i]] = name_to_dept[matches[i]]
        elif i <= 51:
            print(f"{string.ascii_uppercase[i - 26]}: {matches[i]}:\t{name_to_dept[matches[i]]}")
            option_to_dept[string.ascii_uppercase[i - 26]] = name_to_dept[matches[i]]
        else:
            i = 51
            break

    while True:
        if len(matches) == 0:
            print("No matches found.")
            user_input = input(f"Enter manual dept number for {pdf_name}: ")
        else:
            user_input = input(f"Enter selection letter or custom dept number for {pdf_name}: ")
        if not user_input.isdigit() and len(user_input) == 1:
            result = option_to_dept[user_input]
        else:
            result = user_input
        confirm = input(f"you chose dept number: {result} for {pdf_name}. is this correct? [Y/n]: ")
        if (confirm.lower() == "y" or confirm == ""):
            return result

def prompt_src_dir():
    valid_dir = False
    while not valid_dir:
        src_dir = input("Enter directory path containing paystub pdf and name-to-department mapping txt: ")
        valid_dir = True
        if not os.path.exists(src_dir):
            print("File path doesn't exist")
            valid_dir = False
            continue
        if not os.path.isdir(src_dir):
            print("Not a directory.")
            valid_dir = False
    return src_dir

def prompt_paystubs_pdf():
    raw_paystubs_name = input("Enter filename of paystub pdf: ")
    paystubs_pdf = os.path.join(src_dir, raw_paystubs_name)
    if not os.path.exists(paystubs_pdf):
        sys.exit("pdf does not exist")
    if not os.path.isfile(paystubs_pdf):
        sys.exit("pdf is not a file")
    return paystubs_pdf

def find_first_pdf(dir):
    for file in os.listdir(dir):
        if file.lower().endswith(".pdf"):
            return os.path.join(dir, file)
    return None

def prompt_name_dept_map_txt():
    name_dept_map_name = input("Enter filename of name-to-department mapping txt: ")
    name_dept_map_txt = os.path.join(src_dir, name_dept_map_name)
    if not os.path.exists(name_dept_map_txt):
        sys.exit("txt does not exist")
    if not os.path.isfile(name_dept_map_txt):
        sys.exit("not a file")
    return name_dept_map_txt

# try to load config.json that holds previous run file names
if (os.path.exists(CONFIG_JSON) and os.path.isfile(CONFIG_JSON)):
    with open(CONFIG_JSON, "r") as config_file:
        print(f"Located config.json at: {CONFIG_JSON}")
        try:
            config = json.load(config_file)
            src_dir = config["lastSrcDir"]
            if os.path.isdir(src_dir):
                choice = input(f"Sources directory found at: {src_dir}. Use it? [Y/n]: ")
                if (choice.lower() != "y" and choice != ""):
                    src_dir = prompt_src_dir()
            else:
                print(f"Path from config file is not a directory: {src_dir}")
                src_dir = prompt_src_dir()

            paystubs_pdf = find_first_pdf(src_dir)
            if os.path.isfile(paystubs_pdf):
                choice = input(f"Paystubs file found at: {paystubs_pdf}. Use it? [Y/n]: ")
                if (choice.lower() != "y" and choice != ""):
                    paystubs_pdf = prompt_paystubs_pdf()
            else:
                print(f"Path from config file is not a file: {paystubs_pdf}")
                paystubs_pdf = prompt_paystubs_pdf()

            name_dept_map_txt = os.path.join(src_dir, config["lastDeptMapName"])
            if os.path.isfile(name_dept_map_txt):
                choice = input(f"Name-dept mapping .txt found at: {name_dept_map_txt}. Use it? [Y/n]: ")
                if (choice.lower() != "y" and choice != ""):
                    name_dept_map_txt = prompt_name_dept_map_txt()
            else:
                print(f"Path from config file is not a file: {name_dept_map_txt}")
                name_dept_map_txt = prompt_name_dept_map_txt()
        except Exception as ex:
            print("Error parsing config json")
            src_dir = prompt_src_dir()
            paystubs_pdf = prompt_paystubs_pdf()
            name_dept_map_txt = prompt_name_dept_map_txt()
else:
    print("No config.json detected")
    src_dir = prompt_src_dir()
    paystubs_pdf = prompt_paystubs_pdf()
    name_dept_map_txt = prompt_name_dept_map_txt()

# save last inputs to json. querying CONFIG_JSON after this will cause unintended behavior
json_export = {
    "lastSrcDir": os.path.abspath(src_dir),
    "lastPaystubsName": os.path.basename(paystubs_pdf),
    "lastDeptMapName": os.path.basename(name_dept_map_txt)
}
with open(CONFIG_JSON, "w") as config_file:
    json.dump(json_export, config_file)

# grab 20XX_PP from input file name
year_pp = os.path.basename(paystubs_pdf)[0:os.path.basename(paystubs_pdf).find("_")]
if len(year_pp) < 6:
    year = input("Enter year: ")
    pay_period = input("Enter 2-digit pay period: ")
else:
    year = year_pp[0:4]
    pay_period = year_pp[6:8]
    confirm = input(f"Is this correct? Year: {year}, Pay Period: {pay_period}. [Y/n]: ")
    if confirm.lower() != "y" and confirm != "":
        year = input("Enter year: ")
        pay_period = input("Enter 2-digit pay period: ")


# parse txt into hashmap
# note: names in map follow: "lowerfirst lowerlast"
# name grabbing from pdf must be converted to lower() to query values in the map
depts = {} # name -> department map
with open(name_dept_map_txt, "r") as txt:
    line_num = 1
    for line in txt:
        split = line.split(",")
        if len(split) != 4:
            sys.exit("line " + line_num + " when split by ',' resulted in array of length " + len(split) + ". Expected: 4")
        depts[split[0].lower() + " " + split[1].lower()] = split[2]
        line_num += 1
print("-------------------------------------------------------------")

# redact all Orlando...
# need to create the file with redacts because redacting on the fly doesn't work
paystubs_pdf_redacted_path = os.path.join(src_dir, f"{year}PP{pay_period}_paystubs_redacted.pdf")

with pymupdf.open(paystubs_pdf) as doc:
    page_num = -1
    total_redactions = 0
    for page in doc:
        page_num += 1
        # redact "Orlando FL 32830"
        areas = page.search_for("Orlando FL 32830")
        for area in areas:
            adjusted_area = pymupdf.Rect(area.x0, area.y0 + 3, area.x1, area.y1 - 5)  # Shrink the vertical space slightly
            page.add_redact_annot(adjusted_area)
            # page.add_redact_annot(adjusted_area, fill=(0,0,0)) # shows a black box over the redaction region, for debugging purposes
            print(f"Orlando FL 32830 was found and removed from page: {page_num}")
        page.apply_redactions()
        
        if len(areas) > 0:
            total_redactions += 1
    print(f"Number of pages that had contents redacted: {total_redactions}")
    doc.save(paystubs_pdf_redacted_path)
    print(f"Saved as: {paystubs_pdf_redacted_path}")
    print("-------------------------------------------------------------")


do_this_for_all_remaining_items = -1 # -2 = never show again, -1 = unset, 0 = don't overwrite, 1 = overwrite
depts_pdf = {} # mapping of department num/string -> department pdf writer/buffer
with pymupdf.open(paystubs_pdf_redacted_path) as doc:
    page_num = -1
    for page in doc:
        page_num += 1 # check continue statements if moving this statement
        # grab name from pdf page
        parsed_names = [get_name(page).lower(), get_name1(page).lower()]
        if len(set(parsed_names)) == 1: # all names from each parse method match
            name_on_pdf = parsed_names[0]
        else:
            print(f"Multiple candidates found for employee name on page {page_num}")
            name_on_pdf = prompt_selection_or_custom(parsed_names, "name").lower()
        print(f"Name on page {page_num}: {name_on_pdf}")
        # get dept associated with the name
        if name_on_pdf in depts:
            dept = depts[name_on_pdf]
        else:
            print(f"No department number mapping found for name: {name_on_pdf}")
            # find names that may be matches to avoid making the user enter manually
            name_on_pdf_parts = re.split(r"[ -]", name_on_pdf)
            # list of full names from txt that are potential matches
            matches = list(set(fullname for fullname in depts if any(part in re.split(r"[ -]", fullname) for part in name_on_pdf_parts)))
            dept = prompt_selection_or_custom_dept(name_on_pdf, matches, depts)

        # export separate page
        individual_pdf_name = f"pstb_{year}PP{pay_period}_{dept}_{name_on_pdf.replace(" ", "_")}.pdf"
        individual_pdf_path = os.path.join(src_dir, individual_pdf_name)
        overwrite = ""
        if (do_this_for_all_remaining_items == -1 or do_this_for_all_remaining_items == -2) and os.path.exists(individual_pdf_path):
            overwrite = input(f"{individual_pdf_path} already exists. overwrite? [y/N]: ")
            if do_this_for_all_remaining_items != -2:
                do_this_choice = input("Do this for all remaining items? [y/N]: ")
                if do_this_choice.lower() == "y" and overwrite.lower() == "y":
                    do_this_for_all_remaining_items = 1
                elif do_this_choice.lower() == "y" and overwrite.lower() != "y":
                    do_this_for_all_remaining_items = 0
                else:
                    never_show_again = input("Don't ask to do this for all remaining items again this session [y/N]: ")
                    if never_show_again.lower() == "y":
                        do_this_for_all_remaining_items = -2
        if not os.path.exists(individual_pdf_path) or do_this_for_all_remaining_items == 1 or overwrite.lower() == "y":
            individual_pdf = pymupdf.open()
            individual_pdf.insert_pdf(
                docsrc=doc,
                from_page=page_num,
                to_page=page_num,
                start_at=0,
                rotate=0,
                links=True,
                annots=True,
                widgets=True,
                join_duplicates=False,
                show_progress=0,
                final=True
            )
            individual_pdf.save(individual_pdf_path)
            individual_pdf.close()
            print(f"saved as: {individual_pdf_path}")
            print("-------------------------------------------------------------")
        # write to department pdf
        # create pymupdf buffer if there isn't already one in depts_pdf map
        if not dept in depts_pdf:
            depts_pdf[dept] = pymupdf.open()
        # insert page to dept pdf
        depts_pdf[dept].insert_pdf(
            docsrc=doc,
            from_page=page_num,
            to_page=page_num,
            start_at=len(depts_pdf[dept]),
            rotate=0,
            links=True,
            annots=True,
            widgets=True,
            join_duplicates=False,
            show_progress=0,
            final=True
        )
print("Exporting department pdfs:")
for dept, buffer in depts_pdf.items():
    dept_pdf_path = os.path.join(src_dir, f"{year}PP{pay_period}_{dept}_released.pdf")
    overwrite = "y"
    if os.path.exists(dept_pdf_path) and os.path.isfile(dept_pdf_path):
        overwrite = input(f"{dept_pdf_path} already exists. Overwrite? [y/N]: ")
    if overwrite == "y":
        buffer.save(dept_pdf_path)
        print(f"Saved as: {dept_pdf_path}")
    buffer.close()
print("Finished")
