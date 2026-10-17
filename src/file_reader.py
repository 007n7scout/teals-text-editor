def read_file(file_path):
     try:
         with open(file_path, "r") as file:
              return file.read()
     except FileNotFoundError:
          print(f"File at {file_path} was not found! :(")
          return ""

def write_file(file_path, file_content):
     try:
          with open(file_path, "w") as file:
               file.write(file_content)
     except FileNotFoundError:
          print(f"File at {file_path} was not found! :(")