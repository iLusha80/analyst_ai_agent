import os

def concatenate_python_files(input_directory: str, output_file_name: str = "all_python_files.txt", separator: str = "\n\n" + "="*80 + "\n\n"):
    """
    Объединяет содержимое всех файлов .py в указанной директории и ее поддиректориях
    в один текстовый файл. Перед содержимым каждого файла добавляется его полный путь.

    Args:
        input_directory (str): Путь к корневой директории для поиска файлов .py.
        output_file_name (str): Имя файла, в который будет записано объединенное содержимое.
        separator (str): Разделитель, который будет добавлен между содержимым файлов.
    """
    with open(output_file_name, "w", encoding="utf-8") as outfile:
        for root, _, files in os.walk(input_directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    relative_filepath = os.path.relpath(filepath, start=os.getcwd())
                    outfile.write(f"# {relative_filepath}\n")
                    try:
                        with open(filepath, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                        outfile.write(separator)
                    except Exception as e:
                        outfile.write(f"# Ошибка при чтении файла {relative_filepath}: {e}\n")
                        outfile.write(separator)

if __name__ == "__main__":
    # Пример использования:
    # Замените '.' на путь к вашей целевой директории, если она отличается
    input_dir = "frontend-streamlit" 
    output_file = "concatenated_python_code.txt"
    concatenate_python_files(input_dir, output_file)
    print(f"Все файлы .py из директории '{input_dir}' объединены в '{output_file}'")