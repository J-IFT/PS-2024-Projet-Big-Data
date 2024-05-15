import os
from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# Route pour la page index
@app.route('/')
def index():
    # Lister les fichiers TXT disponibles dans le dossier output
    books = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    for i, file_name in enumerate(os.listdir(output_dir)):
        if file_name.startswith("book_") and file_name.endswith(".txt"):
            books.append(f"Livre {i}")
    return render_template('index.html', books=books)

# Route pour la page de résultat
@app.route('/result', methods=['POST'])
def result():
    # Obtenir le livre sélectionné depuis la requête POST
    selected_book_index = int(request.form['selected_book_index'])

    # Vérifier si le fichier TXT correspondant au livre sélectionné existe
    selected_book_file = f"book_{selected_book_index}.txt"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
    selected_book_path = os.path.join(output_dir, selected_book_file)
    if not os.path.exists(selected_book_path):
        return render_template('error.html', message="Le fichier sélectionné n'existe pas.")

    # Lire le fichier TXT correspondant au livre sélectionné
    with open(selected_book_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Vérifier si le fichier CSV correspondant au livre sélectionné existe dans le dossier output/analyse
    csv_file = f"book_{selected_book_index}-occurrence.csv"
    csv_path = os.path.join(output_dir, "analyse", csv_file)
    if not os.path.exists(csv_path):
        return render_template('error.html', message="Le fichier CSV correspondant n'existe pas.")

    # Lire le fichier CSV correspondant au livre sélectionné
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    # Préparer les données pour le graphique d'occurrence des mots
    words = [row[0] for row in data]
    occurrences = [int(row[1]) for row in data]

    # Renvoyer les données à la page result.html
    return render_template('result.html', selected_book=selected_book_file, text=text, words=words, occurrences=occurrences)

if __name__ == '__main__':
    app.run(debug=True)
