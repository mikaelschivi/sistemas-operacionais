import threading
import string
import os

lock = threading.Lock() # fix do print errado

def get_txt_files(path):
    txt_files = []
    files = os.listdir(input_dir)
    print("arquivos do diretorio:", files)
    for f in files:
        fm = f.split(".")
        if fm[1] == "txt":
            txt_files.append(os.path.join(path, f))
    print(f"arquivos texto: {txt_files}")
    return txt_files

def parse_file(id, path):
    with lock:
        print(f"\nTHREAD {id}:")
        data = ""
        with open(path, "r") as f:
            data = f.read()
        
        content = get_content_stats(path, data)
        for k, v in content.items():
            print(f"{k}: {v}")
        
def get_content_stats(path, data):
    words = data.split()
    num_words = len(words)

    vowels = "aeiouAEIOU"
    consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    vowel_counts = {}
    consonant_counts = {}
    word_counts = {}

    for char in data:
        if char in vowels:
            c = char.lower()
            vowel_counts[c] = vowel_counts.get(c, 0) + 1
        elif char in consonants:
            c = char.lower()
            consonant_counts[c] = consonant_counts.get(c, 0) + 1

    for word in words:
        clean = word.strip(string.punctuation).lower()
        if clean:
            word_counts[clean] = word_counts.get(clean, 0) + 1

    most_word = max(word_counts.items(), key=lambda x: x[1])[0] if word_counts else ""
    most_vowel = max(vowel_counts.items(), key=lambda x: x[1])[0] if vowel_counts else ""
    most_consonant = max(consonant_counts.items(), key=lambda x: x[1])[0] if consonant_counts else ""

    dir_path = os.path.dirname(path)
    filename = os.path.basename(path)
    upper_filename = f"{filename}"
    upper_path = os.path.join(dir_path, upper_filename)

    with open(upper_path, "w", encoding="utf-8") as f_upper:
        f_upper.write(data.upper())

    return {
        "arquivo" : path.split("/")[1],
        "palavras": num_words,
        "vogais": sum(vowel_counts.values()),
        "consoantes": sum(consonant_counts.values()),
        "palavra mais usada": most_word,
        "vogal mais usada": most_vowel,
        "consoante mais usada": most_consonant
    }

if __name__ == "__main__":
    # input_dir = input("Nome do diretorio de texto:")
    input_dir = "data"
    if not os.path.exists(input_dir):
        print(f"O arquivo `{input_dir}` não existe no diretório base.")
        exit()
    
    txt_list = get_txt_files(input_dir)

    threads = []
    for id in range(len(txt_list)):    
        t = threading.Thread(target=parse_file, args=(id, txt_list[id],))
        t.start()
        threads.append(t)

    for t in threads:
        t