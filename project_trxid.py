import re
import pandas as pd

# File path of the text file
file_path = "C:\\Users\\User\\Downloads\\donation_info.txt"

# Read the content from the file
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Function to clean and preserve relevant multi-line messages
def clean_and_preserve_multiline(text):
    lines = text.splitlines()
    cleaned_lines = []
    skip_next_lines = 0

    for i, line in enumerate(lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
        
        # Identify and preserve the 5-line "remittance" messages from any source
        if line.startswith("You have received remittance"):
            if i + 4 < len(lines):  # Ensure there are enough lines ahead
                # Combine these 5 lines into one and append
                combined_message = "\n".join(lines[i:i+5])
                cleaned_lines.append(combined_message)
                skip_next_lines = 4  # Skip the next 4 lines
        # Preserve messages starting with the specified prefixes
        elif line.startswith("You have received Tk") or line.startswith("You have received deposit") or line.startswith("Cash In"):
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines)

# Clean the text
cleaned_text = clean_and_preserve_multiline(text)

# Regular expression to remove the day name and time in the second line
cleaned_text = re.sub(r'\n\s*\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b,.*?([AP]M)\s*\n', '\n', cleaned_text)

# Write the cleaned content back to the same file (or a new file if desired)
with open(file_path, "w", encoding="utf-8") as file:
    file.write(cleaned_text)

print("The text has been cleaned.")

# Initialize lists to store the extracted information
amount = []
trxID = []
time = []

# Function to extract the necessary information from a paragraph
def extract_info(paragraph):
    # Initialize variables to store the extracted data
    extracted_amount = None
    extracted_trxid = None
    extracted_time = None
    
    for line in paragraph:
        # Remove the '\u202f' character by replacing it with a standard space
        line = line.replace("\u202f", " ")
        
        # Extract the amount of taka received, remittance total, or cash in using regex
        taka_match = re.search(r'(?:You have received Tk|Total amount: Tk|Cash In Tk|You have received deposit of Tk) (\d+(?:,\d+)*(\.\d{1,2})?)', line)
        if taka_match:
            # Remove commas from the amount for consistency
            extracted_amount = taka_match.group(1).replace(",", "")
        
        # Extract the TrxID using regex
        trxid_match = re.search(r'TrxID (\w+)', line)
        if trxid_match:
            extracted_trxid = trxid_match.group(1)
        
        # Extract the date and time using regex
        time_match = re.search(r'at (\d{2}/\d{2}/\d{4} \d{2}:\d{2})', line)
        if time_match:
            original_time = time_match.group(1)
            extracted_time = convert_time_format(original_time)
    
    # Ensure each list has the same length by appending None if a value is missing
    amount.append(extracted_amount or "")
    trxID.append(extracted_trxid or "")
    time.append(extracted_time or "")

# Function to convert the time format to a 12-hour format with 3-letter month names
def convert_time_format(time_str):
    # Convert the time string to a datetime object
    time_obj = pd.to_datetime(time_str, format='%d/%m/%Y %H:%M')
    
    # Format the datetime object to the desired format with 3-letter month names
    formatted_time = time_obj.strftime('%d %b %Y, %I:%M %p').upper()
    
    return formatted_time

# Initialize an empty list to store the paragraphs
paragraphs = []
current_paragraph = []

# Process the cleaned text
for line in cleaned_text.splitlines():
    # Check if the line starts a new paragraph with the desired prefixes
    if line.startswith("You have received Tk") or line.startswith("You have received deposit") or line.startswith("You have received remittance") or line.startswith("Cash In"):
        # If there is an ongoing paragraph, save it first
        if current_paragraph:
            paragraphs.append(current_paragraph)
            current_paragraph = []  # Start a new paragraph
    
    # Add the line to the current_paragraph
    current_paragraph.append(line.strip())
    
    # Check if the line marks the end of a paragraph (based on "TrxID")
    if "TrxID" in line:
        paragraphs.append(current_paragraph)
        current_paragraph = []  # Reset for the next paragraph

# If there's any remaining paragraph, add it
if current_paragraph:
    paragraphs.append(current_paragraph)

# Now each paragraph is in 'paragraphs' list, where each element is a list of lines.
# Create separate lists like list1, list2, etc.

for i, paragraph in enumerate(paragraphs, start=1):
    globals()[f'list{i}'] = paragraph
    print(f'list{i} = {paragraph}\n')  # Print each list for verification
    
    # Extract and print the corresponding amount, TrxID, and time
    extract_info(paragraph)

# Create a DataFrame from the extracted information
df = pd.DataFrame({
    'Amount': amount,
    'Trx ID': trxID,
    'Time': time
})

# Specify the CSV file path
csv_file_path = "C:\\Users\\User\\Downloads\\extracted_info.csv"

# Write the DataFrame to a CSV file
df.to_csv(csv_file_path, index=False)

print(f"Data has been written to {csv_file_path}")
