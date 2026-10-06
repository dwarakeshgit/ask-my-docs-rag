from file_detector import detect_file_type


test_files = [
    "report.pdf",
    "notes.docx",
    "information.txt",
    "README.md",
    "students.csv",
    "marks.xlsx",
    "old_marks.xls",
    "presentation.pptx",
    "webpage.html",
]


for file_name in test_files:
    file_type = detect_file_type(file_name)
    print(f"{file_name} -> {file_type}")