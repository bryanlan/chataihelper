import re
import json

import re

def fully_escape_string_for_json(original_content):
    # Use json.dumps to produce a valid JSON string. This handles:
    # - Newlines as \\n
    # - Quotes as \"
    # - Backslashes as \\
    # The result is a quoted JSON string, e.g. "some content"
    dumped = json.dumps(original_content)
    
    # Replace '=' with '\u003d' to escape equals signs if needed
    # (This is not strictly necessary for JSON validity, but you requested it.)
    dumped = dumped.replace('=', '\\u003d')
    
    # Remove the surrounding quotes from the JSON string returned by json.dumps()
    # json.dumps() always returns something like: "some content"
    # We just want the inner escaped content without the outer quotes
    return dumped[1:-1]

def fix_full_content(json_str):
    # This regex matches: "full_content": "<content>"
    # and captures <content> in group(2).
    pattern = r'("full_content"\s*:\s*")(.*?)(")'

    def repl(match):
        original_content = match.group(2)
        escaped_content = fully_escape_string_for_json(original_content)
        return f'"full_content": "{escaped_content}"'
    
    return re.sub(pattern, repl, json_str, flags=re.DOTALL)
