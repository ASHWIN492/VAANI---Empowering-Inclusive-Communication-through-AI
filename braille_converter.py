braille_to_text_mapping = {
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e', '⠋': 'f', '⠛': 'g', '⠓': 'h',
    '⠊': 'i', '⠚': 'j', '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o', '⠏': 'p',
    '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't', '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x',
    '⠽': 'y', '⠵': 'z', '⠼': '#', '⠀': ' '
}

def braille_to_text(braille_text):
    plain_text = ''
    for char in braille_text:
        if char in braille_to_text_mapping:
            plain_text += braille_to_text_mapping[char]
        else:
            plain_text += char
    return plain_text