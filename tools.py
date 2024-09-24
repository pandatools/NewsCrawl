import re
def remove_tags(text):
    # Regular expression to match HTML/XML tags
    tag_pattern = re.compile(r'<[^>]+>')
    # Replace all tags with an empty string
    cleaned_text = tag_pattern.sub('', text)
    return cleaned_text