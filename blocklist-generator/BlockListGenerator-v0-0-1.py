# Preparing a blocklist CSV file in multiple languages for personal information filtering

import csv

# File path for saving the blocklist

file_path = "blocklist_azure_openai.csv"

# Updated blocklist patterns with "ExactMatch" or "Regex" type
regex_blocklist_data = [
    # Slovak
    ("\\d{1,3}(,\\d{3})*(\\.\\d{2})?\\s?(EUR|USD|Kč|£)", "Regex"),
    ("\\d{3}-\\d{3}-\\d{3}|\\d{4}\\s\\d{3}\\s\\d{3}", "Regex"),
    ("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "Regex"),
    ("(\\d{1,5}\\s\\w+\\s\\w+|\\w+\\s\\d{1,5})", "Regex"),
    ("P\\.?O\\.?\\sBox\\s\\d+", "Regex"),

    # English
    ("\\d{1,3}(,\\d{3})*(\\.\\d{2})?\\s?(EUR|USD|Kč|£)", "Regex"),
    ("\\d{3}-\\d{3}-\\d{3}|\\d{4}\\s\\d{3}\\s\\d{3}", "Regex"),
    ("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "Regex"),
    ("(\\d{1,5}\\s\\w+\\s\\w+|\\w+\\s\\d{1,5})", "Regex"),
    ("P\\.?O\\.?\\sBox\\s\\d+", "Regex"),

    # German
    ("\\d{1,3}(,\\d{3})*(\\.\\d{2})?\\s?(EUR|USD|Kč|£)", "Regex"),
    ("\\d{3}-\\d{3}-\\d{3}|\\d{4}\\s\\d{3}\\s\\d{3}", "Regex"),
    ("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "Regex"),
    ("(\\d{1,5}\\s\\w+\\s\\w+|\\w+\\s\\d{1,5})", "Regex"),
    ("P\\.?O\\.?\\sBox\\s\\d+", "Regex"),

    # French
    ("\\d{1,3}(,\\d{3})*(\\.\\d{2})?\\s?(EUR|USD|Kč|£)", "Regex"),
    ("\\d{3}-\\d{3}-\\d{3}|\\d{4}\\s\\d{3}\\s\\d{3}", "Regex"),
    ("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "Regex"),
    ("(\\d{1,5}\\s\\w+\\s\\w+|\\w+\\s\\d{1,5})", "Regex"),
    ("P\\.?O\\.?\\sBox\\s\\d+", "Regex")
]

exact_blocklist_data = [
    ("Plat", "ExactMatch"),
    ("Telefónne číslo", "ExactMatch"),
    ("E-mail", "ExactMatch"),
    ("Adresa", "ExactMatch"),
    ("Salary", "ExactMatch"),
    ("Phone Number", "ExactMatch"),
    ("Email", "ExactMatch"),
    ("Address", "ExactMatch"),
    ("Gehalt", "ExactMatch"),
    ("Telefonnummer", "ExactMatch"),
    ("E-Mail", "ExactMatch"),
    ("Adresse", "ExactMatch"),
    ("Salaire", "ExactMatch"),
    ("Numéro de téléphone", "ExactMatch"),
    ("E-mail", "ExactMatch"),
    ("Adresse", "ExactMatch")
]


# Write the updated blocklist to the CSV file
with open(file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Term", "Type"])  # Header row
    writer.writerows(regex_blocklist_data)
    writer.writerows(exact_blocklist_data)

file.close()
file_path = ""
