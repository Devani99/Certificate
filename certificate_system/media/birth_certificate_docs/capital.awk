#!/usr/bin/gawk -f

# Capitalize the first letter of each word
function capitalize(word) {
    return toupper(substr(word, 1, 1)) substr(word, 2)
}

# Process each line of input
{
    # Split the line into words
    n = split($0, words, " ")

    # Capitalize each word and join them
    output = ""
    for (i = 1; i <= n; i++) {
        output = output capitalize(words[i])
        if (i < n) {
            output = output " "  # Add space between words
        }
    }

    # Print the joined, capitalized line
    print output
}

