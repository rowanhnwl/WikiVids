import openai

# Get the authorization key
gptf = open('authorization/gpt.txt', 'r')
key = gptf.read()

openai.api_key = key

# Get the full script
def get_script(title, wc):
    
    # Generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"user", "content":"Write a roughly " + str(wc) + " word summary about " + title + " (the rock), divided into paragraphs with no titles."}
        ] 
    )

    # Get and return the script
    script = response.choices[0].message["content"]
    return script

# Split the full text into paragraphs
def split_paragraphs(text):
    
    # Split into paragraphs
    paragraphs = text.split("\n\n", -1)
    return paragraphs

# Get the summary of a given paragraph
def get_summary(text):

    # Generate a one-word summary
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"user", "content":"Using five words or less, determine a short title for this script: " + text}
        ]
    )

    # Get and return the summary
    summary = response.choices[0].message["content"]
    
    # Remove quotations if they exist
    if summary[0] == chr(34):
        summary = summary[1:-1]

    return summary

# Remove any generated titles in the script
def remove_titles(paragraphs, threshold):
    
    # Iterate through paragraphs and remove paragraphs less than a certain number of words
    for pg in paragraphs:
        wc = len(pg.split(" "))

        if wc < threshold:
            paragraphs.remove(pg)

    return paragraphs