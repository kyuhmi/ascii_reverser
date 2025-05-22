import argparse
import json
from typing import TextIO

def read_file_to_list(file_path):
    """Reads lines from a file into a list.

    Args:
      file_path: The path to the file.

    Returns:
      A list of strings, where each string is a line from the file.
      Returns an empty list if the file cannot be opened.
    """
    try:
        with open(file_path, 'r') as f:
          return f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")  # Optional error message
        return []

def strip_right_from_each(strings):
    return list(map(str.rstrip, strings))

def get_max_len_str(strings):
    return max([ len(s) for s in strings ])

def add_padding_to_strings(strings, target_len):
    return [ s + " " * (target_len - len(s)) for s in strings ]

def mirror_line(line, char_map):
    chr_mapping_fn = lambda c: char_map[c]
    result = "".join(reversed("".join(map(chr_mapping_fn, line))))
    return result

def preprocess_and_mirror_lines(lines, char_map):
    max_len = get_max_len_str(lines)
    preprocessed_lines = add_padding_to_strings(strip_right_from_each(lines), max_len)
    print("preprocessed:") # debug
    [print(line) for line in preprocessed_lines]
    result = list(map(lambda line: mirror_line(line, char_map), preprocessed_lines))
    return result

def write_list_to_file(data, filename):
    """Writes a list of strings to a file.
    Args:
        data: A list of strings.
        filename: The name of the file to write to.
    """
    with open(filename, "w") as f:
        for item in data:
            f.write(item + "\n")

def unique_characters(strings):
    """
    Returns a set of unique characters from a list of strings.
    """
    unique_chars = set()
    for s in strings:
        for char in s:
            unique_chars.add(char)
    return unique_chars

def load_character_map(json_file):
    """Loads a character map from a JSON file.

    Args:
      json_file: Path to the JSON file.

    Returns:
      A dictionary mapping characters to characters, or None if an error occurred.
    """
    try:
        with open(json_file, 'r') as f:
            char_map = json.load(f)
        return char_map
    except FileNotFoundError:
        print(f"Error: File not found: {json_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file}")
        return None

def write_character_map(char_map, json_file):
    """Writes a character map to a JSON file.

    Args:
      char_map: A dictionary mapping characters to characters.
      json_file: Path to the JSON file.

    Returns:
      True if the character map was written successfully, False otherwise.
    """
    try:
        with open(json_file, 'w') as f:
            json.dump(char_map, f, indent=4)
        return True
    except Exception as e:
        print(f"Error writing to {json_file}: {e}")
        return False

def prompt_user_to_create_template():
    while True:
        input_char = input("Would you like to write an empty json map? [Y/n]: ").strip().lower()[0]
        if input_char in ['y', 'n']:
            if input_char == 'y':
                return True
            else:
                return False
        else:
            print("Invalid input. Try again.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Character mapper for flipping ASCII art")
    parser.add_argument('-m', '--application-mode',
                        choices=['uniq', 'map'],
                        help="Application mode (uniq or map)",
                        default='map')
    parser.add_argument('-f', '--ascii-filepath', help="Text file with ASCII art")
    parser.add_argument('-j', '--map-filepath', help="JSON file with mappings for each character to a visually reversed character")
    parser.add_argument('-o', '--output-filepath', help="Output file for reversed ASCII art or character map template")

    args = parser.parse_args()

    if args.application_mode == 'map' and not args.map_filepath:
        parser.error("--map-filepath is required when application mode is 'map'")

    return args.application_mode, args.ascii_filepath, args.map_filepath, args.output_filepath

def main():
    mode, input_filepath, map_filepath, output_filepath = parse_arguments()

    if mode == 'map':
        unique_chars = unique_characters(read_file_to_list(input_filepath))
        character_map = load_character_map(map_filepath)

        if not unique_chars.issubset(character_map.keys()):
            missing_chars = unique_chars - character_map.keys()
            print(f"Mappings missing for characters: {missing_chars}")
            print("Please add them and run the program again.")
            return

        lines = read_file_to_list(input_filepath)
        mirrored_lines = preprocess_and_mirror_lines(lines, character_map)
        print("Result:")
        [ print(line) for line in mirrored_lines ]

        if output_filepath is not None:
            write_list_to_file(mirrored_lines, output_filepath)
            print(f"Written output to {output_filepath}")

    elif mode == 'uniq':
        unique_chars = unique_characters(read_file_to_list(input_filepath))
        print(f"Unique Characters: {unique_chars}")
        if output_filepath is not None and prompt_user_to_create_template():
            # make dict with chars with empty keys
            template_dict = { char : '' for char in unique_chars }
            write_character_map(template_dict, output_filepath)
            print(f"Written template to {output_filepath}")
    else:
        print(f"Mode {mode} not recognized.")

if __name__ == "__main__":
    main()
